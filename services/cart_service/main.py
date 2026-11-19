from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine
from services.common.models import CartItemModel, ProductModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "cart-service"

app = FastAPI(title="Shopping Cart Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class AddToCartRequest(BaseModel):
    product_id: int
    quantity: Optional[int] = 1
    user_id: Optional[int] = None
    session_id: Optional[str] = "guest-session"

class UpdateCartRequest(BaseModel):
    product_id: int
    quantity: int
    user_id: Optional[int] = None
    session_id: Optional[str] = "guest-session"

def get_cart_filter(user_id: Optional[int], session_id: Optional[str]):
    if user_id:
        return CartItemModel.user_id == user_id
    return CartItemModel.session_id == (session_id or "guest-session")

@app.get("/")
def get_cart(
    user_id: Optional[int] = None,
    session_id: Optional[str] = "guest-session",
    db: Session = Depends(get_db)
):
    filter_cond = get_cart_filter(user_id, session_id)
    items = db.query(CartItemModel).filter(filter_cond).all()

    formatted_items = []
    subtotal = 0.0
    item_count = 0

    for item in items:
        p = item.product
        if not p:
            continue
        effective_price = round(p.price * (1 - (p.discount_pct / 100.0)), 2)
        item_total = round(effective_price * item.quantity, 2)
        subtotal += item_total
        item_count += item.quantity

        formatted_items.append({
            "cart_item_id": item.id,
            "product_id": p.id,
            "name": p.name,
            "slug": p.slug,
            "category": p.category,
            "brand": p.brand,
            "price": p.price,
            "discount_pct": p.discount_pct,
            "effective_price": effective_price,
            "quantity": item.quantity,
            "item_total": item_total,
            "image_url": p.image_url,
            "available_stock": p.stock,
            "in_stock": p.stock >= item.quantity
        })

    return {
        "items": formatted_items,
        "item_count": item_count,
        "subtotal": round(subtotal, 2),
        "user_id": user_id,
        "session_id": session_id
    }

@app.post("/add")
def add_to_cart(req: AddToCartRequest, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    filter_cond = get_cart_filter(req.user_id, req.session_id)
    existing_item = db.query(CartItemModel).filter(
        filter_cond,
        CartItemModel.product_id == req.product_id
    ).first()

    if existing_item:
        existing_item.quantity += req.quantity
    else:
        new_item = CartItemModel(
            user_id=req.user_id,
            session_id=req.session_id,
            product_id=req.product_id,
            quantity=req.quantity
        )
        db.add(new_item)

    db.commit()

    event_bus.publish_event(
        event_type="cart.updated",
        payload={"action": "add", "product_id": req.product_id, "user_id": req.user_id},
        source_service=SERVICE_NAME
    )

    return get_cart(user_id=req.user_id, session_id=req.session_id, db=db)

@app.put("/update")
def update_cart_item(req: UpdateCartRequest, db: Session = Depends(get_db)):
    filter_cond = get_cart_filter(req.user_id, req.session_id)
    item = db.query(CartItemModel).filter(
        filter_cond,
        CartItemModel.product_id == req.product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if req.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = req.quantity

    db.commit()

    event_bus.publish_event(
        event_type="cart.updated",
        payload={"action": "update", "product_id": req.product_id, "user_id": req.user_id},
        source_service=SERVICE_NAME
    )

    return get_cart(user_id=req.user_id, session_id=req.session_id, db=db)

@app.delete("/remove/{product_id}")
def remove_from_cart(
    product_id: int,
    user_id: Optional[int] = None,
    session_id: Optional[str] = "guest-session",
    db: Session = Depends(get_db)
):
    filter_cond = get_cart_filter(user_id, session_id)
    item = db.query(CartItemModel).filter(
        filter_cond,
        CartItemModel.product_id == product_id
    ).first()

    if item:
        db.delete(item)
        db.commit()

    return get_cart(user_id=user_id, session_id=session_id, db=db)

@app.delete("/clear")
def clear_cart(
    user_id: Optional[int] = None,
    session_id: Optional[str] = "guest-session",
    db: Session = Depends(get_db)
):
    filter_cond = get_cart_filter(user_id, session_id)
    db.query(CartItemModel).filter(filter_cond).delete()
    db.commit()
    return {"message": "Cart cleared", "items": [], "subtotal": 0.0, "item_count": 0}
