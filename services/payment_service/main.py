import uuid
import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine
from services.common.models import PaymentTransactionModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "payment-service"

app = FastAPI(title="Payment Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class ProcessPaymentRequest(BaseModel):
    order_id: str
    user_id: int
    amount: float
    currency: Optional[str] = "INR"
    payment_method: str # CARD, UPI, NETBANKING, COD
    card_number: Optional[str] = None
    upi_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    simulate_failure: Optional[bool] = False

class RefundRequest(BaseModel):
    transaction_id: str
    order_id: str
    amount: float
    reason: Optional[str] = "Order Cancelled"

@app.post("/process")
def process_payment(req: ProcessPaymentRequest, db: Session = Depends(get_db)):
    # 1. Check idempotency
    if req.idempotency_key:
        existing = db.query(PaymentTransactionModel).filter(
            PaymentTransactionModel.idempotency_key == req.idempotency_key
        ).first()
        if existing:
            return {
                "transaction_id": existing.transaction_id,
                "order_id": existing.order_id,
                "status": existing.status,
                "amount": existing.amount,
                "is_idempotent_replay": True
            }

    txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

    # 2. Check failure simulation request
    if req.simulate_failure:
        failed_txn = PaymentTransactionModel(
            transaction_id=txn_id,
            order_id=req.order_id,
            user_id=req.user_id,
            amount=req.amount,
            currency=req.currency or "INR",
            status="FAILED",
            payment_method=req.payment_method,
            idempotency_key=req.idempotency_key,
            error_reason="Payment authorization failed: Insufficient funds or bank timeout"
        )
        db.add(failed_txn)
        db.commit()

        event_bus.publish_event(
            event_type="payment.failed",
            payload={"transaction_id": txn_id, "order_id": req.order_id, "amount": req.amount, "reason": failed_txn.error_reason},
            source_service=SERVICE_NAME,
            transaction_id=txn_id
        )

        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment processing failed: Transaction declined by issuing bank"
        )

    # 3. Successful transaction
    gateway_ref = f"GATEWAY-REF-{uuid.uuid4().hex[:8].upper()}"
    txn = PaymentTransactionModel(
        transaction_id=txn_id,
        order_id=req.order_id,
        user_id=req.user_id,
        amount=req.amount,
        currency=req.currency or "INR",
        status="SUCCESS",
        payment_method=req.payment_method,
        gateway_ref=gateway_ref,
        idempotency_key=req.idempotency_key
    )
    db.add(txn)
    db.commit()

    event_bus.publish_event(
        event_type="payment.success",
        payload={
            "transaction_id": txn_id,
            "order_id": req.order_id,
            "amount": req.amount,
            "payment_method": req.payment_method,
            "gateway_ref": gateway_ref
        },
        source_service=SERVICE_NAME,
        transaction_id=txn_id
    )

    return {
        "status": "SUCCESS",
        "transaction_id": txn_id,
        "order_id": req.order_id,
        "amount": req.amount,
        "currency": req.currency,
        "gateway_ref": gateway_ref,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.post("/refund")
def process_refund(req: RefundRequest, db: Session = Depends(get_db)):
    refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"
    refund_txn = PaymentTransactionModel(
        transaction_id=refund_id,
        order_id=req.order_id,
        user_id=1,
        amount=req.amount,
        currency="INR",
        status="REFUNDED",
        payment_method="REFUND",
        gateway_ref=f"REFUND-FOR-{req.transaction_id}",
        error_reason=req.reason
    )
    db.add(refund_txn)
    db.commit()

    event_bus.publish_event(
        event_type="refund.processed",
        payload={"refund_id": refund_id, "order_id": req.order_id, "amount": req.amount, "reason": req.reason},
        source_service=SERVICE_NAME
    )

    return {
        "status": "REFUNDED",
        "refund_id": refund_id,
        "order_id": req.order_id,
        "amount": req.amount,
        "message": f"Refund of ₹{req.amount:.2f} processed successfully."
    }

@app.get("/transactions")
def get_transactions(user_id: Optional[int] = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(PaymentTransactionModel)
    if user_id:
        query = query.filter(PaymentTransactionModel.user_id == user_id)
    txns = query.order_by(PaymentTransactionModel.created_at.desc()).limit(limit).all()

    return [{
        "transaction_id": t.transaction_id,
        "order_id": t.order_id,
        "amount": t.amount,
        "currency": t.currency,
        "status": t.status,
        "payment_method": t.payment_method,
        "gateway_ref": t.gateway_ref,
        "created_at": t.created_at.isoformat()
    } for t in txns]
