from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from services.common.database import get_db, Base, engine
from services.common.models import UserModel, ProductModel, OrderModel, PaymentTransactionModel, SupportTicketModel, ShipmentModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.telemetry import telemetry_collector

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "admin-service"

app = FastAPI(title="Administration Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

@app.get("/overview")
def get_admin_overview(db: Session = Depends(get_db)):
    total_users = db.query(UserModel).count()
    total_products = db.query(ProductModel).count()
    total_orders = db.query(OrderModel).count()
    low_stock_count = db.query(ProductModel).filter(ProductModel.stock < 10).count()
    open_tickets = db.query(SupportTicketModel).filter(SupportTicketModel.status.in_(["OPEN", "IN_PROGRESS"])).count()
    revenue = db.query(func.sum(OrderModel.final_amount)).filter(OrderModel.status.in_(["CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED"])).scalar() or 0.0

    return {
        "total_revenue": round(revenue, 2),
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "low_stock_count": low_stock_count,
        "open_support_tickets": open_tickets,
        "services_health": telemetry_collector.get_service_health()
    }

@app.get("/users")
def get_users(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset((page - 1) * limit).limit(limit).all()
    return [{
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "phone": u.phone,
        "created_at": u.created_at.isoformat()
    } for u in users]

@app.get("/products")
def get_admin_products(category: Optional[str] = None, page: int = 1, limit: int = 30, db: Session = Depends(get_db)):
    query = db.query(ProductModel)
    if category:
        query = query.filter(ProductModel.category == category)
    total = query.count()
    products = query.order_by(ProductModel.id.asc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "products": [{
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "brand": p.brand,
            "price": p.price,
            "discount_pct": p.discount_pct,
            "stock": p.stock,
            "rating": p.rating,
            "image_url": p.image_url
        } for p in products]
    }

@app.get("/orders")
def get_admin_orders(status_filter: Optional[str] = None, page: int = 1, limit: int = 25, db: Session = Depends(get_db)):
    query = db.query(OrderModel)
    if status_filter:
        query = query.filter(OrderModel.status == status_filter)
    total = query.count()
    orders = query.order_by(OrderModel.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "orders": [{
            "id": o.id,
            "order_number": o.order_number,
            "user_id": o.user_id,
            "status": o.status,
            "final_amount": o.final_amount,
            "payment_method": o.payment_method,
            "payment_status": o.payment_status,
            "items_count": len(o.items),
            "created_at": o.created_at.isoformat()
        } for o in orders]
    }
