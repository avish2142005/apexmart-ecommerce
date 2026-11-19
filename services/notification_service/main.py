import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine, SessionLocal
from services.common.models import NotificationRecordModel, UserModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "notification-service"

app = FastAPI(title="Notification Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class SendNotificationRequest(BaseModel):
    user_id: int
    notification_type: str # ORDER_CONFIRMATION, PAYMENT_SUCCESS, PAYMENT_FAILED, SHIPMENT_UPDATE, DELIVERY_ALERT
    recipient: str # Email or phone
    channel: Optional[str] = "EMAIL" # EMAIL, SMS, PUSH
    title: str
    content: str

def record_notification(user_id: int, notif_type: str, recipient: str, channel: str, title: str, content: str):
    db = SessionLocal()
    try:
        record = NotificationRecordModel(
            user_id=user_id,
            notification_type=notif_type,
            recipient=recipient,
            channel=channel,
            title=title,
            content=content,
            status="SENT",
            sent_at=datetime.datetime.utcnow()
        )
        db.add(record)
        db.commit()
    finally:
        db.close()

# Event bus subscriptions
def on_order_created(event):
    payload = event.get("payload", {})
    user_id = payload.get("user_id", 1)
    order_num = payload.get("order_number", "")
    amount = payload.get("final_amount", 0.0)
    record_notification(
        user_id=user_id,
        notif_type="ORDER_CONFIRMATION",
        recipient=f"user-{user_id}@example.com",
        channel="EMAIL",
        title=f"Order Confirmed: {order_num}",
        content=f"Thank you! Your order {order_num} for ₹{amount:.2f} has been placed successfully and is being prepared."
    )

def on_payment_success(event):
    payload = event.get("payload", {})
    order_num = payload.get("order_id", "")
    amount = payload.get("amount", 0.0)
    txn = payload.get("transaction_id", "")
    record_notification(
        user_id=1,
        notif_type="PAYMENT_SUCCESS",
        recipient="+919876543210",
        channel="SMS",
        title="Payment Received",
        content=f"Payment of ₹{amount:.2f} received for Order {order_num}. Reference: {txn}."
    )

def on_shipment_created(event):
    payload = event.get("payload", {})
    order_num = payload.get("order_number", "")
    tracking = payload.get("tracking_number", "")
    carrier = payload.get("carrier", "Carrier")
    record_notification(
        user_id=1,
        notif_type="SHIPMENT_UPDATE",
        recipient="user@example.com",
        channel="EMAIL",
        title=f"Order {order_num} has shipped!",
        content=f"Great news! Your package is on its way via {carrier}. Tracking number: {tracking}."
    )

event_bus.subscribe("order.created", on_order_created)
event_bus.subscribe("payment.success", on_payment_success)
event_bus.subscribe("shipment.created", on_shipment_created)

@app.post("/send")
def send_notification(req: SendNotificationRequest, db: Session = Depends(get_db)):
    notif = NotificationRecordModel(
        user_id=req.user_id,
        notification_type=req.notification_type,
        recipient=req.recipient,
        channel=req.channel or "EMAIL",
        title=req.title,
        content=req.content,
        status="SENT",
        sent_at=datetime.datetime.utcnow()
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    return {
        "status": "SENT",
        "notification_id": notif.id,
        "recipient": notif.recipient,
        "channel": notif.channel,
        "sent_at": notif.sent_at.isoformat()
    }

@app.get("/history")
def get_user_notifications(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    notifs = db.query(NotificationRecordModel).filter(
        NotificationRecordModel.user_id == user_id
    ).order_by(NotificationRecordModel.sent_at.desc()).limit(limit).all()

    return [{
        "id": n.id,
        "type": n.notification_type,
        "channel": n.channel,
        "recipient": n.recipient,
        "title": n.title,
        "content": n.content,
        "status": n.status,
        "sent_at": n.sent_at.isoformat()
    } for n in notifs]
