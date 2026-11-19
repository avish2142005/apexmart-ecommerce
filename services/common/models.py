import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from services.common.database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="customer") # customer, admin, support_agent
    phone = Column(String(50), index=True, nullable=True)
    address_street = Column(String(255), nullable=True)
    address_city = Column(String(100), nullable=True)
    address_state = Column(String(100), nullable=True)
    address_zip = Column(String(20), nullable=True)
    address_country = Column(String(100), default="India")
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), index=True, nullable=False)
    brand = Column(String(100), index=True, nullable=False)
    price = Column(Float, nullable=False)
    discount_pct = Column(Float, default=0.0)
    stock = Column(Integer, default=50)
    rating = Column(Float, default=4.5)
    rating_count = Column(Integer, default=12)
    image_url = Column(String(500), nullable=False)
    images_json = Column(Text, default="[]")
    specs_json = Column(Text, default="{}")
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CartItemModel(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    session_id = Column(String(100), index=True, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    product = relationship("ProductModel")

class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    status = Column(String(50), default="PLACED") # PLACED, CONFIRMED, PROCESSING, SHIPPED, OUT_FOR_DELIVERY, DELIVERED, CANCELLED, RETURNED
    subtotal = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    shipping_fee = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    shipping_address_json = Column(Text, nullable=False)
    payment_method = Column(String(50), default="CARD") # CARD, UPI, NETBANKING, COD
    payment_status = Column(String(50), default="PENDING") # PENDING, SUCCESS, FAILED, REFUNDED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    items = relationship("OrderItemModel", back_populates="order")

class OrderItemModel(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    image_url = Column(String(500), nullable=True)

    order = relationship("OrderModel", back_populates="items")

class PaymentTransactionModel(Base):
    __tablename__ = "payment_transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    order_id = Column(String(50), index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="SUCCESS") # SUCCESS, FAILED, PENDING, REFUNDED
    payment_method = Column(String(50), nullable=False)
    gateway_ref = Column(String(100), nullable=True)
    idempotency_key = Column(String(100), unique=True, index=True, nullable=True)
    error_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ShipmentModel(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(100), unique=True, index=True, nullable=False)
    order_number = Column(String(50), index=True, nullable=False)
    tracking_number = Column(String(100), unique=True, index=True, nullable=False)
    carrier = Column(String(100), default="Amazon Logistics") # FedEx, BlueDart, DHL, Amazon Logistics
    status = Column(String(50), default="LABEL_CREATED") # LABEL_CREATED, PICKED_UP, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, FAILED
    estimated_delivery = Column(DateTime, nullable=True)
    current_location = Column(String(255), default="Central Fulfillment Hub, Bengaluru")
    milestones_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class SupportTicketModel(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    user_email = Column(String(255), nullable=False)
    order_number = Column(String(50), nullable=True)
    subject = Column(String(255), nullable=False)
    category = Column(String(100), default="Order Issue") # Order Issue, Payment, Refund, Return, Product Inquiry, Technical
    message = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN") # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(50), default="MEDIUM") # LOW, MEDIUM, HIGH, URGENT
    responses_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ReviewModel(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    user_name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False) # 1-5
    title = Column(String(255), nullable=False)
    comment = Column(Text, nullable=False)
    verified_purchase = Column(Boolean, default=True)
    helpful_votes = Column(Integer, default=0)
    status = Column(String(50), default="APPROVED") # APPROVED, PENDING, REJECTED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CouponModel(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_type = Column(String(20), default="PERCENTAGE") # PERCENTAGE, FIXED
    discount_value = Column(Float, nullable=False)
    min_order_value = Column(Float, default=0.0)
    max_discount = Column(Float, default=10000.0)
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

class InventoryReservationModel(Base):
    __tablename__ = "inventory_reservations"
    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(String(100), unique=True, index=True, nullable=False)
    order_id = Column(String(50), index=True, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), default="RESERVED") # RESERVED, CONFIRMED, RELEASED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class NotificationRecordModel(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    notification_type = Column(String(100), nullable=False)
    recipient = Column(String(255), nullable=False)
    channel = Column(String(50), default="EMAIL") # EMAIL, SMS, PUSH
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="SENT")
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
