import json
import uuid
import datetime
import random
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine
from services.common.models import ShipmentModel, OrderModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "shipping-service"

app = FastAPI(title="Shipping and Delivery Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

CARRIERS = ["Amazon Logistics", "BlueDart Express", "Delhivery", "FedEx", "DHL Express"]

class CreateShipmentRequest(BaseModel):
    order_number: str
    recipient_name: str
    shipping_address: dict
    carrier: Optional[str] = None

class UpdateDeliveryStatusRequest(BaseModel):
    status: str # LABEL_CREATED, PICKED_UP, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, FAILED
    location: str
    note: Optional[str] = None

def format_shipment(s: ShipmentModel) -> dict:
    return {
        "shipment_id": s.shipment_id,
        "order_number": s.order_number,
        "tracking_number": s.tracking_number,
        "carrier": s.carrier,
        "status": s.status,
        "estimated_delivery": s.estimated_delivery.isoformat() if s.estimated_delivery else None,
        "current_location": s.current_location,
        "milestones": json.loads(s.milestones_json) if s.milestones_json else [],
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat()
    }

@app.post("/create", status_code=status.HTTP_201_CREATED)
def create_shipment(req: CreateShipmentRequest, db: Session = Depends(get_db)):
    # Check if shipment already exists
    existing = db.query(ShipmentModel).filter(ShipmentModel.order_number == req.order_number).first()
    if existing:
        return format_shipment(existing)

    carrier = req.carrier or random.choice(CARRIERS)
    shipment_id = f"SHIP-{uuid.uuid4().hex[:8].upper()}"
    tracking_number = f"TRK-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:6].upper()}"

    now = datetime.datetime.utcnow()
    eta = now + datetime.timedelta(days=3)

    initial_milestones = [
        {
            "status": "ORDER_PLACED",
            "title": "Order Placed and Confirmed",
            "location": "Warehouse Fulfillment Center",
            "timestamp": now.isoformat(),
            "completed": True
        },
        {
            "status": "LABEL_CREATED",
            "title": "Shipping Label Created",
            "location": "Central Fulfillment Hub, Bengaluru",
            "timestamp": (now + datetime.timedelta(minutes=15)).isoformat(),
            "completed": True
        },
        {
            "status": "PICKED_UP",
            "title": f"Picked up by {carrier}",
            "location": "Bengaluru Sort Facility",
            "timestamp": (now + datetime.timedelta(hours=2)).isoformat(),
            "completed": False
        },
        {
            "status": "IN_TRANSIT",
            "title": "Package In Transit to Delivery Station",
            "location": "Regional Hub",
            "timestamp": (now + datetime.timedelta(days=1)).isoformat(),
            "completed": False
        },
        {
            "status": "OUT_FOR_DELIVERY",
            "title": "Out for Delivery",
            "location": "Local Delivery Station",
            "timestamp": (now + datetime.timedelta(days=2)).isoformat(),
            "completed": False
        },
        {
            "status": "DELIVERED",
            "title": "Delivered to Customer",
            "location": req.shipping_address.get("city", "Customer Destination"),
            "timestamp": eta.isoformat(),
            "completed": False
        }
    ]

    shipment = ShipmentModel(
        shipment_id=shipment_id,
        order_number=req.order_number,
        tracking_number=tracking_number,
        carrier=carrier,
        status="LABEL_CREATED",
        estimated_delivery=eta,
        current_location="Central Fulfillment Hub, Bengaluru",
        milestones_json=json.dumps(initial_milestones)
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    event_bus.publish_event(
        event_type="shipment.created",
        payload={
            "shipment_id": shipment_id,
            "order_number": req.order_number,
            "tracking_number": tracking_number,
            "carrier": carrier,
            "estimated_delivery": eta.isoformat()
        },
        source_service=SERVICE_NAME
    )

    return format_shipment(shipment)

@app.get("/track/{tracking_number_or_order}")
def track_shipment(tracking_number_or_order: str, db: Session = Depends(get_db)):
    shipment = db.query(ShipmentModel).filter(
        (ShipmentModel.tracking_number == tracking_number_or_order) |
        (ShipmentModel.order_number == tracking_number_or_order)
    ).first()

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment tracking not found")
    return format_shipment(shipment)

@app.put("/update-status/{tracking_number}")
def update_delivery_status(tracking_number: str, req: UpdateDeliveryStatusRequest, db: Session = Depends(get_db)):
    shipment = db.query(ShipmentModel).filter(ShipmentModel.tracking_number == tracking_number).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipment.status = req.status
    shipment.current_location = req.location

    # Update milestone list
    milestones = json.loads(shipment.milestones_json) if shipment.milestones_json else []
    for m in milestones:
        if m["status"] == req.status:
            m["completed"] = True
            m["timestamp"] = datetime.datetime.utcnow().isoformat()
            if req.note:
                m["title"] += f" ({req.note})"
    shipment.milestones_json = json.dumps(milestones)

    # If delivered, also update Order status
    if req.status == "DELIVERED":
        order = db.query(OrderModel).filter(OrderModel.order_number == shipment.order_number).first()
        if order:
            order.status = "DELIVERED"
        event_bus.publish_event(
            event_type="shipment.delivered",
            payload={"tracking_number": tracking_number, "order_number": shipment.order_number},
            source_service=SERVICE_NAME
        )

    db.commit()
    db.refresh(shipment)
    return format_shipment(shipment)

@app.get("/carriers")
def get_carriers():
    return [
        {"name": "Amazon Logistics", "speed": "1-2 Business Days", "coverage": "Nationwide Pan-India"},
        {"name": "BlueDart Express", "speed": "Next Day Air", "coverage": "Metro & Tier-1 Cities"},
        {"name": "Delhivery", "speed": "2-3 Days Ground", "coverage": "All 19,000+ Pincodes"},
        {"name": "FedEx Priority", "speed": "2 Days Express", "coverage": "Major Hubs"},
        {"name": "DHL Express", "speed": "Same Day / Next Day", "coverage": "Commercial Hubs"}
    ]
