from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.common.database import get_db, Base, engine
from services.common.models import CouponModel
from services.common.middleware import ObservabilityMiddleware, setup_standard_routes

Base.metadata.create_all(bind=engine)

SERVICE_NAME = "pricing-service"

app = FastAPI(title="Pricing & Promotion Service", version="1.0.0")
app.add_middleware(ObservabilityMiddleware, service_name=SERVICE_NAME)
setup_standard_routes(app, SERVICE_NAME)

class PriceItem(BaseModel):
    product_id: int
    price: float
    quantity: int

class PriceCalculationRequest(BaseModel):
    items: List[PriceItem]
    coupon_code: Optional[str] = None
    shipping_pincode: Optional[str] = None

class ValidateCouponRequest(BaseModel):
    code: str
    order_amount: float

@app.post("/calculate")
def calculate_pricing(req: PriceCalculationRequest, db: Session = Depends(get_db)):
    subtotal = sum(item.price * item.quantity for item in req.items)
    
    # 1. Coupon discount
    discount_amount = 0.0
    coupon_applied = None

    if req.coupon_code:
        coupon = db.query(CouponModel).filter(
            CouponModel.code == req.coupon_code.upper().strip(),
            CouponModel.active == True
        ).first()

        if coupon:
            if subtotal >= coupon.min_order_value:
                if coupon.discount_type == "PERCENTAGE":
                    calculated_disc = (subtotal * coupon.discount_value) / 100.0
                    discount_amount = min(calculated_disc, coupon.max_discount)
                else: # FIXED
                    discount_amount = min(coupon.discount_value, subtotal)
                
                coupon_applied = {
                    "code": coupon.code,
                    "discount_value": coupon.discount_value,
                    "discount_type": coupon.discount_type,
                    "saved_amount": round(discount_amount, 2)
                }

    # 2. Shipping calculation: Free if subtotal - discount >= 499, else 49
    net_after_discount = max(0.0, subtotal - discount_amount)
    shipping_fee = 0.0 if net_after_discount >= 499.0 or (coupon_applied and coupon_applied["code"] == "FREESHIP") else 49.0

    # 3. Tax calculation: Standard 18% GST on net taxable value
    tax_rate_pct = 18.0
    # Price is tax-inclusive or calculated on net: here we show explicit GST component breakdown
    tax_amount = round(net_after_discount * (tax_rate_pct / 100.0) / (1 + (tax_rate_pct / 100.0)), 2)

    final_amount = round(net_after_discount + shipping_fee, 2)

    return {
        "subtotal": round(subtotal, 2),
        "discount_amount": round(discount_amount, 2),
        "coupon_applied": coupon_applied,
        "tax_amount": tax_amount,
        "tax_rate_pct": tax_rate_pct,
        "shipping_fee": round(shipping_fee, 2),
        "free_shipping_eligible": shipping_fee == 0.0,
        "amount_needed_for_free_shipping": max(0.0, round(499.0 - net_after_discount, 2)),
        "final_amount": final_amount
    }

@app.post("/coupon/validate")
def validate_coupon(req: ValidateCouponRequest, db: Session = Depends(get_db)):
    coupon = db.query(CouponModel).filter(
        CouponModel.code == req.code.upper().strip(),
        CouponModel.active == True
    ).first()

    if not coupon:
        raise HTTPException(status_code=400, detail="Invalid coupon code")

    if req.order_amount < coupon.min_order_value:
        raise HTTPException(
            status_code=400,
            detail=f"Coupon requires a minimum order value of ₹{coupon.min_order_value:.2f}"
        )

    if coupon.discount_type == "PERCENTAGE":
        savings = min((req.order_amount * coupon.discount_value) / 100.0, coupon.max_discount)
    else:
        savings = min(coupon.discount_value, req.order_amount)

    return {
        "valid": True,
        "code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "savings": round(savings, 2),
        "message": f"Coupon applied! You save ₹{savings:.2f}"
    }

@app.get("/coupons")
def list_available_coupons(db: Session = Depends(get_db)):
    coupons = db.query(CouponModel).filter(CouponModel.active == True).all()
    return [{
        "code": c.code,
        "discount_type": c.discount_type,
        "discount_value": c.discount_value,
        "min_order_value": c.min_order_value,
        "description": f"Get {c.discount_value}% OFF up to ₹{c.max_discount}" if c.discount_type == "PERCENTAGE" else f"Flat ₹{c.discount_value} OFF"
    } for c in coupons]
