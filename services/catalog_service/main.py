import json
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from services.common.database import get_db, Base, engine
from services.common.models import ProductModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "catalog-service"

app = FastAPI(title="Product Catalog Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class ProductCreateRequest(BaseModel):
    name: str
    slug: str
    description: str
    category: str
    brand: str
    price: float
    discount_pct: Optional[float] = 0.0
    stock: Optional[int] = 50
    image_url: str
    images_json: Optional[str] = "[]"
    specs_json: Optional[str] = "{}"
    is_featured: Optional[bool] = False

def format_product(p: ProductModel) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "category": p.category,
        "brand": p.brand,
        "price": p.price,
        "discount_pct": p.discount_pct,
        "discounted_price": round(p.price * (1 - (p.discount_pct / 100.0)), 2),
        "stock": p.stock,
        "in_stock": p.stock > 0,
        "rating": p.rating,
        "rating_count": p.rating_count,
        "image_url": p.image_url,
        "images": json.loads(p.images_json) if p.images_json else [p.image_url],
        "specs": json.loads(p.specs_json) if p.specs_json else {},
        "is_featured": p.is_featured,
        "created_at": p.created_at.isoformat()
    }

@app.get("/products")
def list_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: Optional[bool] = False,
    sort_by: Optional[str] = "featured", # price_asc, price_desc, rating, newest, featured
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ProductModel)

    if category and category.lower() != "all":
        query = query.filter(ProductModel.category.ilike(category))
    if brand:
        query = query.filter(ProductModel.brand.ilike(brand))
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)
    if in_stock_only:
        query = query.filter(ProductModel.stock > 0)

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(ProductModel.price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(ProductModel.price))
    elif sort_by == "rating":
        query = query.order_by(desc(ProductModel.rating))
    elif sort_by == "newest":
        query = query.order_by(desc(ProductModel.created_at))
    else: # featured
        query = query.order_by(desc(ProductModel.is_featured), desc(ProductModel.rating))

    total = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "products": [format_product(p) for p in products]
    }

@app.get("/products/{id_or_slug}")
def get_product(id_or_slug: str, db: Session = Depends(get_db)):
    if id_or_slug.isdigit():
        product = db.query(ProductModel).filter(ProductModel.id == int(id_or_slug)).first()
    else:
        product = db.query(ProductModel).filter(ProductModel.slug == id_or_slug).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product '{id_or_slug}' not found")
    return format_product(product)

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    all_products = db.query(ProductModel.category).all()
    counts = {}
    for (cat,) in all_products:
        counts[cat] = counts.get(cat, 0) + 1

    category_list = []
    category_icons = {
        "Smartphones": "Smartphone",
        "Laptops": "Laptop",
        "Audio & Headphones": "Headphones",
        "Smart Watches": "Watch",
        "Cameras & Photography": "Camera",
        "Televisions & Home Theater": "Tv",
        "Computer Accessories": "HardDrive",
        "Gaming Consoles & Gear": "Gamepad2",
        "Home Appliances": "Zap",
        "Kitchen Appliances": "Coffee",
        "Smart Home & Security": "ShieldCheck",
        "Furniture": "Armchair",
        "Men's Fashion": "Shirt",
        "Women's Fashion": "Sparkles",
        "Footwear": "Footprints",
        "Sports & Fitness": "Dumbbell",
        "Books & Media": "BookOpen",
        "Beauty & Personal Care": "HeartHandshake",
        "Health & Wellness": "Activity",
        "Automotive & Tools": "Wrench"
    }

    for cat_name, count in sorted(counts.items(), key=lambda x: x[0]):
        category_list.append({
            "name": cat_name,
            "count": count,
            "icon": category_icons.get(cat_name, "Tag")
        })

    return category_list

@app.get("/featured")
def get_featured(db: Session = Depends(get_db)):
    featured = db.query(ProductModel).filter(ProductModel.is_featured == True).limit(8).all()
    deals = db.query(ProductModel).filter(ProductModel.discount_pct >= 20).order_by(desc(ProductModel.discount_pct)).limit(8).all()
    top_rated = db.query(ProductModel).filter(ProductModel.rating >= 4.5).order_by(desc(ProductModel.rating_count)).limit(8).all()

    return {
        "featured": [format_product(p) for p in featured],
        "deals_of_the_day": [format_product(p) for p in deals],
        "top_rated": [format_product(p) for p in top_rated]
    }

@app.get("/products/{product_id}/recommendations")
def get_recommendations(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Recommend products in the same category
    same_cat = db.query(ProductModel).filter(
        ProductModel.category == product.category,
        ProductModel.id != product.id
    ).limit(6).all()

    # Fallback to other high-rated items
    if len(same_cat) < 4:
        others = db.query(ProductModel).filter(ProductModel.id != product.id).order_by(desc(ProductModel.rating)).limit(6 - len(same_cat)).all()
        same_cat.extend(others)

    return [format_product(p) for p in same_cat]

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(req: ProductCreateRequest, db: Session = Depends(get_db)):
    p = ProductModel(
        name=req.name,
        slug=req.slug,
        description=req.description,
        category=req.category,
        brand=req.brand,
        price=req.price,
        discount_pct=req.discount_pct or 0.0,
        stock=req.stock or 50,
        image_url=req.image_url,
        images_json=req.images_json or "[]",
        specs_json=req.specs_json or "{}",
        is_featured=req.is_featured or False
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    event_bus.publish_event(
        event_type="product.created",
        payload={"product_id": p.id, "name": p.name, "category": p.category, "price": p.price},
        source_service=SERVICE_NAME
    )
    return format_product(p)
