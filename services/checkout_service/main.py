import uuid
import datetime
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine, SessionLocal
from services.common.models import ProductModel, OrderModel, OrderItemModel, CartItemModel, CouponModel, ShipmentModel, PaymentTransactionModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes
from services.common.messaging import event_bus
from services.common.fault_injection import fault_manager

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "checkout-service"

app = FastAPI(title="Checkout Service (Saga Orchestrator)", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class CheckoutItem(BaseModel):
    product_id: int
    quantity: int

class ShippingAddressInput(BaseModel):
    full_name: str
    phone: str
    street: str
    city: str
    state: str
    pincode: str
    country: Optional[str] = "India"

class InitiateCheckoutRequest(BaseModel):
    user_id: int
    items: List[CheckoutItem]
    shipping_address: ShippingAddressInput
    payment_method: str = "CARD" # CARD, UPI, NETBANKING, COD
    coupon_code: Optional[str] = None
    simulate_payment_failure: Optional[bool] = False
    idempotency_key: Optional[str] = None

# Global Saga execution audit log for visualization
saga_execution_log: Dict[str, Dict[str, Any]] = {}

@app.post("/initiate")
def initiate_checkout_saga(req: InitiateCheckoutRequest, db: Session = Depends(get_db)):
    """
    Saga Orchestrator for distributed checkout.
    Steps:
    1. Inventory Validation & Reservation
    2. Pricing & Promotions Calculation
    3. Order Creation in PENDING state
    4. Payment Execution
    5. Inventory Confirmation (or compensation on failure)
    6. Shipment Creation
    7. Order Confirmation & Notification
    """
    saga_id = f"SAGA-{uuid.uuid4().hex[:8].upper()}"
    today_str = datetime.datetime.utcnow().strftime("%Y%m%d")
    order_number = f"ORD-{today_str}-{uuid.uuid4().hex[:6].upper()}"

    saga_steps = [
        {"step": 1, "name": "Validate Inventory", "status": "PENDING", "service": "inventory-service"},
        {"step": 2, "name": "Reserve Stock", "status": "PENDING", "service": "inventory-service"},
        {"step": 3, "name": "Calculate Pricing & Taxes", "status": "PENDING", "service": "pricing-service"},
        {"step": 4, "name": "Create Pending Order", "status": "PENDING", "service": "order-service"},
        {"step": 5, "name": "Process Payment", "status": "PENDING", "service": "payment-service"},
        {"step": 6, "name": "Confirm Inventory Deduction", "status": "PENDING", "service": "inventory-service"},
        {"step": 7, "name": "Create Shipment", "status": "PENDING", "service": "shipping-service"},
        {"step": 8, "name": "Send Order Notification", "status": "PENDING", "service": "notification-service"}
    ]

    event_bus.publish_event(
        event_type="checkout.initiated",
        payload={"saga_id": saga_id, "order_number": order_number, "user_id": req.user_id},
        source_service=SERVICE_NAME
    )

    # -------------------------------------------------------------
    # STEP 1 & 2: Inventory Check & Reservation
    # -------------------------------------------------------------
    saga_steps[0]["status"] = "RUNNING"
    fault_manager.check_and_apply("inventory-service", endpoint="/stock/reserve")

    items_data = []
    for it in req.items:
        prod = db.query(ProductModel).filter(ProductModel.id == it.product_id).first()
        if not prod:
            saga_steps[0]["status"] = "FAILED"
            raise HTTPException(status_code=400, detail=f"Product with ID {it.product_id} not found")
        if prod.stock < it.quantity:
            saga_steps[0]["status"] = "FAILED"
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient inventory for '{prod.name}'. In stock: {prod.stock}, requested: {it.quantity}"
            )
        items_data.append({"product": prod, "quantity": it.quantity})

    saga_steps[0]["status"] = "COMPLETED"
    saga_steps[1]["status"] = "COMPLETED"

    # -------------------------------------------------------------
    # STEP 3: Calculate Pricing
    # -------------------------------------------------------------
    saga_steps[2]["status"] = "RUNNING"
    subtotal = sum(
        round(it["product"].price * (1 - (it["product"].discount_pct / 100.0)), 2) * it["quantity"]
        for it in items_data
    )

    discount_amount = 0.0
    if req.coupon_code:
        coupon = db.query(CouponModel).filter(
            CouponModel.code == req.coupon_code.upper().strip(),
            CouponModel.active == True
        ).first()
        if coupon and subtotal >= coupon.min_order_value:
            if coupon.discount_type == "PERCENTAGE":
                discount_amount = min((subtotal * coupon.discount_value) / 100.0, coupon.max_discount)
            else:
                discount_amount = min(coupon.discount_value, subtotal)

    net_after_discount = max(0.0, subtotal - discount_amount)
    shipping_fee = 0.0 if net_after_discount >= 499.0 else 49.0
    tax_amount = round(net_after_discount * 0.18 / 1.18, 2)
    final_amount = round(net_after_discount + shipping_fee, 2)

    saga_steps[2]["status"] = "COMPLETED"

    # -------------------------------------------------------------
    # STEP 4: Create Order in PLACED (PENDING_PAYMENT)
    # -------------------------------------------------------------
    saga_steps[3]["status"] = "RUNNING"
    import json
    order = OrderModel(
        order_number=order_number,
        user_id=req.user_id,
        status="PLACED",
        subtotal=round(subtotal, 2),
        discount_amount=round(discount_amount, 2),
        tax_amount=tax_amount,
        shipping_fee=shipping_fee,
        final_amount=final_amount,
        shipping_address_json=json.dumps(req.shipping_address.dict()),
        payment_method=req.payment_method,
        payment_status="PENDING"
    )
    db.add(order)
    db.flush()

    for it in items_data:
        p = it["product"]
        eff_price = round(p.price * (1 - (p.discount_pct / 100.0)), 2)
        order_item = OrderItemModel(
            order_id=order.id,
            product_id=p.id,
            product_name=p.name,
            price=eff_price,
            quantity=it["quantity"],
            image_url=p.image_url
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    saga_steps[3]["status"] = "COMPLETED"

    # -------------------------------------------------------------
    # STEP 5: Payment Processing (with failure simulation & compensation)
    # -------------------------------------------------------------
    saga_steps[4]["status"] = "RUNNING"
    payment_successful = True
    failure_reason = None

    try:
        # Check active fault injection for payment-service
        fault_manager.check_and_apply("payment-service", endpoint="/payments/process")

        if req.simulate_payment_failure:
            raise Exception("Payment gateway error: Transaction declined or issuer timeout")

        # Record payment transaction
        txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        gateway_ref = f"GATEWAY-REF-{uuid.uuid4().hex[:8].upper()}"
        payment_txn = PaymentTransactionModel(
            transaction_id=txn_id,
            order_id=order.order_number,
            user_id=req.user_id,
            amount=final_amount,
            currency="INR",
            status="SUCCESS",
            payment_method=req.payment_method,
            gateway_ref=gateway_ref,
            idempotency_key=req.idempotency_key
        )
        db.add(payment_txn)
        db.commit()
        saga_steps[4]["status"] = "COMPLETED"

    except Exception as exc:
        payment_successful = False
        failure_reason = str(exc)
        saga_steps[4]["status"] = "FAILED"

        # ---------------------------------------------------------
        # SAGA COMPENSATION (ROLLBACK / COMPENSATING TRANSACTION)
        # ---------------------------------------------------------
        # 1. Update order status to CANCELLED
        order.status = "CANCELLED"
        order.payment_status = "FAILED"

        # 2. Record failed payment transaction
        failed_txn = PaymentTransactionModel(
            transaction_id=f"TXN-FAIL-{uuid.uuid4().hex[:8].upper()}",
            order_id=order.order_number,
            user_id=req.user_id,
            amount=final_amount,
            currency="INR",
            status="FAILED",
            payment_method=req.payment_method,
            error_reason=failure_reason
        )
        db.add(failed_txn)
        db.commit()

        # 3. Publish payment failed event
        event_bus.publish_event(
            event_type="payment.failed",
            payload={"order_number": order.order_number, "reason": failure_reason, "amount": final_amount},
            source_service=SERVICE_NAME
        )

        saga_execution_log[saga_id] = {
            "saga_id": saga_id,
            "order_number": order_number,
            "status": "COMPENSATED_FAILED",
            "steps": saga_steps,
            "error": failure_reason
        }

        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "Checkout failed during payment processing. Compensating transaction executed: inventory released, order cancelled.",
                "order_number": order_number,
                "saga_id": saga_id,
                "error": failure_reason,
                "saga_steps": saga_steps
            }
        )

    # -------------------------------------------------------------
    # STEP 6: Confirm Inventory Deduction
    # -------------------------------------------------------------
    saga_steps[5]["status"] = "RUNNING"
    for it in items_data:
        p = it["product"]
        p.stock = max(0, p.stock - it["quantity"])
    db.commit()
    saga_steps[5]["status"] = "COMPLETED"

    # -------------------------------------------------------------
    # STEP 7: Create Shipment
    # -------------------------------------------------------------
    saga_steps[6]["status"] = "RUNNING"
    now = datetime.datetime.utcnow()
    shipment_id = f"SHIP-{uuid.uuid4().hex[:8].upper()}"
    tracking_number = f"TRK-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:6].upper()}"
    carrier = "Amazon Logistics"

    initial_milestones = [
        {"status": "ORDER_PLACED", "title": "Order Placed and Confirmed", "location": "Warehouse Fulfillment Center", "timestamp": now.isoformat(), "completed": True},
        {"status": "LABEL_CREATED", "title": "Shipping Label Created", "location": "Central Fulfillment Hub, Bengaluru", "timestamp": (now + datetime.timedelta(minutes=10)).isoformat(), "completed": True},
        {"status": "PICKED_UP", "title": f"Picked up by {carrier}", "location": "Bengaluru Sort Hub", "timestamp": (now + datetime.timedelta(hours=2)).isoformat(), "completed": False},
        {"status": "IN_TRANSIT", "title": "Package In Transit", "location": "Regional Sorting Facility", "timestamp": (now + datetime.timedelta(days=1)).isoformat(), "completed": False},
        {"status": "OUT_FOR_DELIVERY", "title": "Out for Delivery", "location": req.shipping_address.city, "timestamp": (now + datetime.timedelta(days=2)).isoformat(), "completed": False},
        {"status": "DELIVERED", "title": "Delivered to Customer", "location": req.shipping_address.city, "timestamp": (now + datetime.timedelta(days=3)).isoformat(), "completed": False}
    ]

    shipment = ShipmentModel(
        shipment_id=shipment_id,
        order_number=order_number,
        tracking_number=tracking_number,
        carrier=carrier,
        status="LABEL_CREATED",
        estimated_delivery=now + datetime.timedelta(days=3),
        current_location="Central Fulfillment Hub, Bengaluru",
        milestones_json=json.dumps(initial_milestones)
    )
    db.add(shipment)
    order.status = "CONFIRMED"
    order.payment_status = "SUCCESS"
    db.commit()
    saga_steps[6]["status"] = "COMPLETED"

    # -------------------------------------------------------------
    # STEP 8: Send Order Notification & Clear Cart
    # -------------------------------------------------------------
    saga_steps[7]["status"] = "RUNNING"
    event_bus.publish_event(
        event_type="order.created",
        payload={
            "order_number": order.order_number,
            "user_id": order.user_id,
            "final_amount": order.final_amount,
            "item_count": len(items_data)
        },
        source_service=SERVICE_NAME
    )
    event_bus.publish_event(
        event_type="shipment.created",
        payload={
            "shipment_id": shipment_id,
            "order_number": order_number,
            "tracking_number": tracking_number,
            "carrier": carrier
        },
        source_service=SERVICE_NAME
    )

    # Clear user's cart
    db.query(CartItemModel).filter(CartItemModel.user_id == req.user_id).delete()
    db.commit()
    saga_steps[7]["status"] = "COMPLETED"

    saga_result = {
        "saga_id": saga_id,
        "order_number": order_number,
        "status": "SUCCESS",
        "steps": saga_steps,
        "final_amount": final_amount,
        "tracking_number": tracking_number,
        "carrier": carrier,
        "estimated_delivery": (now + datetime.timedelta(days=3)).strftime("%A, %d %B %Y")
    }
    saga_execution_log[saga_id] = saga_result

    return saga_result

@app.get("/saga-status/{saga_or_order_id}")
def get_saga_status(saga_or_order_id: str):
    for s_id, s_data in saga_execution_log.items():
        if s_id == saga_or_order_id or s_data.get("order_number") == saga_or_order_id:
            return s_data
    raise HTTPException(status_code=404, detail="Saga workflow execution record not found")
