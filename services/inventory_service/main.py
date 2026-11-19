import uuid
import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine
from services.common.models import ProductModel, InventoryReservationModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "inventory-service"

app = FastAPI(title="Inventory Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class StockCheckItem(BaseModel):
    product_id: int
    quantity: int

class ReserveStockRequest(BaseModel):
    order_id: str
    items: List[StockCheckItem]
    ttl_seconds: Optional[int] = 600 # 10 minutes

class ConfirmReservationRequest(BaseModel):
    order_id: str

class ReleaseReservationRequest(BaseModel):
    order_id: str
    reason: Optional[str] = "Cancelled or Payment Failed"

class StockUpdateRequest(BaseModel):
    product_id: int
    new_stock: int

@app.get("/stock/{product_id}")
def get_stock(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Determine warehouse
    warehouse = "BLR-FC-01" if product_id % 3 == 0 else ("BOM-FC-04" if product_id % 2 == 0 else "DEL-FC-02")
    return {
        "product_id": product.id,
        "product_name": product.name,
        "available_stock": product.stock,
        "in_stock": product.stock > 0,
        "warehouse": warehouse,
        "is_low_stock": product.stock < 10
    }

@app.post("/check")
def check_stock(items: List[StockCheckItem], db: Session = Depends(get_db)):
    results = []
    all_available = True
    for item in items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            all_available = False
            results.append({
                "product_id": item.product_id,
                "requested": item.quantity,
                "available": product.stock if product else 0,
                "is_available": False
            })
        else:
            results.append({
                "product_id": item.product_id,
                "requested": item.quantity,
                "available": product.stock,
                "is_available": True
            })

    return {
        "all_available": all_available,
        "items": results
    }

@app.post("/reserve")
def reserve_stock(req: ReserveStockRequest, db: Session = Depends(get_db)):
    # Verify all items have enough stock
    for item in req.items:
        p = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not p or p.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient inventory for product '{p.name if p else item.product_id}'. Available: {p.stock if p else 0}, Requested: {item.quantity}"
            )

    reservations = []
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=req.ttl_seconds)

    for item in req.items:
        res_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
        res = InventoryReservationModel(
            reservation_id=res_id,
            order_id=req.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            status="RESERVED",
            expires_at=expires_at
        )
        db.add(res)
        reservations.append(res_id)

    db.commit()

    return {
        "status": "RESERVED",
        "order_id": req.order_id,
        "reservation_ids": reservations,
        "expires_at": expires_at.isoformat()
    }

@app.post("/confirm")
def confirm_reservation(req: ConfirmReservationRequest, db: Session = Depends(get_db)):
    reservations = db.query(InventoryReservationModel).filter(
        InventoryReservationModel.order_id == req.order_id,
        InventoryReservationModel.status == "RESERVED"
    ).all()

    if not reservations:
        return {"status": "NO_ACTIVE_RESERVATIONS", "message": "No reserved stock found for order"}

    for res in reservations:
        res.status = "CONFIRMED"
        product = db.query(ProductModel).filter(ProductModel.id == res.product_id).first()
        if product:
            product.stock = max(0, product.stock - res.quantity)

            # Publish inventory updated event
            event_bus.publish_event(
                event_type="inventory.updated",
                payload={"product_id": product.id, "new_stock": product.stock, "deducted": res.quantity},
                source_service=SERVICE_NAME
            )

            # Check low stock
            if product.stock < 10:
                event_bus.publish_event(
                    event_type="inventory.low_stock",
                    payload={"product_id": product.id, "name": product.name, "current_stock": product.stock, "threshold": 10},
                    source_service=SERVICE_NAME
                )

    db.commit()
    return {"status": "CONFIRMED", "order_id": req.order_id, "confirmed_items": len(reservations)}

@app.post("/release")
def release_reservation(req: ReleaseReservationRequest, db: Session = Depends(get_db)):
    reservations = db.query(InventoryReservationModel).filter(
        InventoryReservationModel.order_id == req.order_id,
        InventoryReservationModel.status == "RESERVED"
    ).all()

    for res in reservations:
        res.status = "RELEASED"

    db.commit()
    return {"status": "RELEASED", "order_id": req.order_id, "released_count": len(reservations), "reason": req.reason}

@app.put("/update")
def update_stock(req: StockUpdateRequest, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.stock = req.new_stock
    db.commit()

    event_bus.publish_event(
        event_type="inventory.updated",
        payload={"product_id": product.id, "new_stock": product.stock},
        source_service=SERVICE_NAME
    )
    return {"product_id": product.id, "name": product.name, "stock": product.stock}

@app.get("/low-stock")
def get_low_stock_products(threshold: int = 10, db: Session = Depends(get_db)):
    products = db.query(ProductModel).filter(ProductModel.stock <= threshold).all()
    return [{
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "stock": p.stock,
        "image_url": p.image_url
    } for p in products]
