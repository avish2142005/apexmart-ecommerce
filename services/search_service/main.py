from typing import Optional, List
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from services.common.database import get_db, Base, engine
from services.common.models import ProductModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "search-service"

app = FastAPI(title="Search Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

@app.get("/query")
def search_products(
    q: str = Query("", description="Search term"),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = "relevance", # relevance, price_asc, price_desc, rating
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ProductModel)

    if q.strip():
        search_terms = q.strip().split()
        for term in search_terms:
            pattern = f"%{term}%"
            query = query.filter(
                or_(
                    ProductModel.name.ilike(pattern),
                    ProductModel.description.ilike(pattern),
                    ProductModel.brand.ilike(pattern),
                    ProductModel.category.ilike(pattern)
                )
            )

    if category and category.lower() != "all":
        query = query.filter(ProductModel.category.ilike(category))
    if brand:
        query = query.filter(ProductModel.brand.ilike(brand))
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(ProductModel.price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(ProductModel.price))
    elif sort_by == "rating":
        query = query.order_by(desc(ProductModel.rating))
    elif sort_by == "newest":
        query = query.order_by(desc(ProductModel.created_at))
    else: # relevance
        query = query.order_by(desc(ProductModel.is_featured), desc(ProductModel.rating))

    total = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    return {
        "query": q,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "results": [{
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "category": p.category,
            "brand": p.brand,
            "price": p.price,
            "discount_pct": p.discount_pct,
            "discounted_price": round(p.price * (1 - (p.discount_pct / 100.0)), 2),
            "rating": p.rating,
            "rating_count": p.rating_count,
            "stock": p.stock,
            "image_url": p.image_url,
            "description": p.description[:120] + "..." if len(p.description) > 120 else p.description
        } for p in products]
    }

@app.get("/suggestions")
def autocomplete_suggestions(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    pattern = f"%{q.strip()}%"
    products = db.query(ProductModel.name, ProductModel.category, ProductModel.brand).filter(
        or_(
            ProductModel.name.ilike(pattern),
            ProductModel.brand.ilike(pattern),
            ProductModel.category.ilike(pattern)
        )
    ).limit(8).all()

    suggestions = []
    seen = set()
    for name, cat, brand in products:
        if name not in seen:
            suggestions.append({"text": name, "type": "product"})
            seen.add(name)
        if brand and brand not in seen:
            suggestions.append({"text": brand, "type": "brand"})
            seen.add(brand)
        if cat and cat not in seen:
            suggestions.append({"text": cat, "type": "category"})
            seen.add(cat)

    return suggestions[:10]
