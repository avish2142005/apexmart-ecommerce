import json
import uuid
import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine
from services.common.models import OrderModel, OrderItemModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "order-service"

app = FastAPI(title="Order Management Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class OrderItemSchema(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    image_url: Optional[str] = None

class CreateOrderRequest(BaseModel):
    user_id: int
    items: List[OrderItemSchema]
    subtotal: float
    discount_amount: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    shipping_fee: Optional[float] = 0.0
    final_amount: float
    shipping_address: dict
    payment_method: str = "CARD"
    order_number: Optional[str] = None

class UpdateOrderStatusRequest(BaseModel):
    status: str

def format_order(order: OrderModel) -> dict:
    return {
        "id": order.id,
        "order_number": order.order_number,
        "user_id": order.user_id,
        "status": order.status,
        "subtotal": order.subtotal,
        "discount_amount": order.discount_amount,
        "tax_amount": order.tax_amount,
        "shipping_fee": order.shipping_fee,
        "final_amount": order.final_amount,
        "shipping_address": json.loads(order.shipping_address_json) if order.shipping_address_json else {},
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "items": [{
            "id": it.id,
            "product_id": it.product_id,
            "product_name": it.product_name,
            "price": it.price,
            "quantity": it.quantity,
            "image_url": it.image_url
        } for it in order.items],
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat()
    }

@app.post("/create", status_code=status.HTTP_201_CREATED)
def create_order(req: CreateOrderRequest, db: Session = Depends(get_db)):
    today_str = datetime.datetime.utcnow().strftime("%Y%m%d")
    order_num = req.order_number or f"ORD-{today_str}-{uuid.uuid4().hex[:6].upper()}"

    order = OrderModel(
        order_number=order_num,
        user_id=req.user_id,
        status="PLACED",
        subtotal=req.subtotal,
        discount_amount=req.discount_amount or 0.0,
        tax_amount=req.tax_amount or 0.0,
        shipping_fee=req.shipping_fee or 0.0,
        final_amount=req.final_amount,
        shipping_address_json=json.dumps(req.shipping_address),
        payment_method=req.payment_method,
        payment_status="PENDING"
    )
    db.add(order)
    db.flush()

    for item in req.items:
        db_item = OrderItemModel(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            price=item.price,
            quantity=item.quantity,
            image_url=item.image_url
        )
        db.add(db_item)

    db.commit()
    db.refresh(order)

    event_bus.publish_event(
        event_type="order.created",
        payload={
            "order_number": order.order_number,
            "user_id": order.user_id,
            "final_amount": order.final_amount,
            "item_count": len(req.items)
        },
        source_service=SERVICE_NAME
    )

    return format_order(order)

@app.get("/")
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(OrderModel).filter(OrderModel.user_id == user_id).order_by(OrderModel.created_at.desc()).all()
    return [format_order(o) for o in orders]

@app.get("/{order_number}")
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return format_order(order)

@app.put("/{order_number}/status")
def update_status(order_number: str, req: UpdateOrderStatusRequest, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = req.status
    if req.status == "CONFIRMED":
        order.payment_status = "SUCCESS"
    elif req.status in ("CANCELLED", "RETURNED"):
        order.payment_status = "REFUNDED"

    db.commit()
    db.refresh(order)
    return format_order(order)

@app.post("/{order_number}/cancel")
def cancel_order(order_number: str, reason: Optional[str] = "Customer request", db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status in ("DELIVERED", "CANCELLED"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status '{order.status}'")

    order.status = "CANCELLED"
    order.payment_status = "REFUNDED"
    db.commit()

    event_bus.publish_event(
        event_type="order.cancelled",
        payload={"order_number": order.order_number, "user_id": order.user_id, "reason": reason},
        source_service=SERVICE_NAME
    )
    return {"message": "Order cancelled successfully", "order_number": order_number, "status": "CANCELLED"}

@app.get("/admin/all")
def get_all_orders(
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(OrderModel)
    if status_filter:
        query = query.filter(OrderModel.status == status_filter)
    total = query.count()
    orders = query.order_by(OrderModel.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "orders": [format_order(o) for o in orders]
    }
