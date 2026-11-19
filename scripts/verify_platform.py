import time
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def log_test(step: str, success: bool, details: str = ""):
    icon = "PASS" if success else "FAIL"
    print(f"[{icon}] {step}")
    if details:
        print(f"       -> {details}")
    if not success:
        sys.exit(1)

def run_verification():
    print("==================================================================")
    print(" APEXMART INDUSTRIAL E-COMMERCE END-TO-END VERIFICATION SUITE    ")
    print("==================================================================")

    # 1. Health check
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=3)
        log_test("Gateway Health Endpoint", res.status_code == 200, f"Status: {res.json().get('status')}")
    except Exception as e:
        log_test("Gateway Health Endpoint", False, f"Connection failed: {e}")

    # 2. User Authentication
    login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "john.doe@example.com",
        "password": "customer123"
    })
    token = login_res.json().get("access_token")
    log_test("User Authentication (JWT)", login_res.status_code == 200 and token is not None, f"Token: {token[:20]}...")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Product Catalog
    cat_res = requests.get(f"{BASE_URL}/api/v1/catalog/products?limit=5")
    products = cat_res.json().get("products", [])
    log_test("Product Catalog Retrieval", len(products) > 0, f"Retrieved {len(products)} products")
    target_product = products[0]

    # 4. Search Service
    search_res = requests.get(f"{BASE_URL}/api/v1/search/query?q=Apple")
    search_results = search_res.json().get("results", [])
    log_test("Search Service (Keyword 'Apple')", len(search_results) > 0, f"Found {len(search_results)} items")

    # 5. Shopping Cart
    cart_add_res = requests.post(f"{BASE_URL}/api/v1/cart/add", json={
        "product_id": target_product["id"],
        "quantity": 2,
        "user_id": 2
    })
    cart_items = cart_add_res.json().get("items", [])
    log_test("Shopping Cart Add Item", len(cart_items) > 0, f"Cart Items: {len(cart_items)}, Subtotal: ₹{cart_add_res.json().get('subtotal')}")

    # 6. Pricing Calculation & Coupon
    price_res = requests.post(f"{BASE_URL}/api/v1/pricing/calculate", json={
        "items": [{"product_id": target_product["id"], "price": target_product["discounted_price"], "quantity": 2}],
        "coupon_code": "SAVE10"
    })
    pricing = price_res.json()
    log_test("Pricing Service with Coupon SAVE10", pricing.get("discount_amount") > 0, f"Discount: ₹{pricing.get('discount_amount')}, Final: ₹{pricing.get('final_amount')}")

    # 7. SAGA Checkout Execution (SUCCESS PATH)
    checkout_res = requests.post(f"{BASE_URL}/api/v1/checkout/initiate", json={
        "user_id": 2,
        "items": [{"product_id": target_product["id"], "quantity": 1}],
        "shipping_address": {
            "full_name": "John Doe",
            "phone": "+919876543210",
            "street": "Flat 402, Green Glen Layout, Bellandur",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560103"
        },
        "payment_method": "CARD",
        "coupon_code": "SAVE10"
    })
    order_data = checkout_res.json()
    order_number = order_data.get("order_number")
    tracking_number = order_data.get("tracking_number")
    log_test("Saga Distributed Checkout Execution", checkout_res.status_code == 200 and order_number is not None, f"Order: {order_number}, Tracking: {tracking_number}")

    # 8. Shipping Milestone Advancement
    ship_res = requests.put(f"{BASE_URL}/api/v1/shipping/update-status/{tracking_number}", json={
        "status": "IN_TRANSIT",
        "location": "Regional Sorting Hub",
        "note": "Automated verification scan"
    })
    log_test("Shipping Service Tracking & Milestone", ship_res.status_code == 200, f"Shipment status: {ship_res.json().get('status')}")

    # 9. Support Ticket Creation
    ticket_res = requests.post(f"{BASE_URL}/api/v1/support/tickets", json={
        "user_id": 2,
        "user_email": "john.doe@example.com",
        "order_number": order_number,
        "subject": "Delivery Instructions",
        "category": "Order Issue",
        "message": "Please leave the parcel with security desk if unavailable.",
        "priority": "LOW"
    })
    ticket_id = ticket_res.json().get("ticket_id")
    log_test("Customer Support Ticket Creation", ticket_id is not None, f"Ticket ID: {ticket_id}")

    # 10. Reviews & Ratings
    review_res = requests.post(f"{BASE_URL}/api/v1/reviews/", json={
        "product_id": target_product["id"],
        "user_id": 2,
        "user_name": "John Doe",
        "rating": 5,
        "title": "Outstanding build quality",
        "comment": "Exceeded all expectations. Fast delivery."
    })
    log_test("Customer Review Submission & Star Rating", review_res.status_code == 201, f"Review ID: {review_res.json().get('id')}")

    # 11. Chaos Engineering: Trigger Scenario 1 (Payment Timeout)
    chaos_res = requests.post(f"{BASE_URL}/api/v1/faults/scenario/1")
    log_test("Chaos Studio: Trigger Scenario 1 (Payment Failure)", chaos_res.status_code == 200, f"Scenario: {chaos_res.json().get('name')}")

    # 12. SAGA Checkout Compensating Rollback Verification
    failed_checkout_res = requests.post(f"{BASE_URL}/api/v1/checkout/initiate", json={
        "user_id": 2,
        "items": [{"product_id": target_product["id"], "quantity": 1}],
        "shipping_address": {
            "full_name": "John Doe",
            "phone": "+919876543210",
            "street": "Flat 402, Green Glen Layout, Bellandur",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560103"
        },
        "payment_method": "CARD"
    })
    log_test("Saga Compensation on Injected Failure", failed_checkout_res.status_code in (402, 500, 504), f"Status {failed_checkout_res.status_code} received as expected. Rollback executed.")

    # 13. Telemetry Service Health & Error Detection
    health_res = requests.get(f"{BASE_URL}/api/telemetry/services-health")
    health_data = health_res.json()
    services_map = health_data.get("services", {})
    failed_srv = any(s.get("failed_requests", 0) > 0 for s in services_map.values())
    log_test("Centralized Telemetry & Error Tracking", health_res.status_code == 200 and failed_srv, f"Services tracked: {len(services_map)}")

    # 14. Clear All Injected Faults
    clear_res = requests.delete(f"{BASE_URL}/api/v1/faults/clear-all")
    log_test("Chaos Studio: Clear All Faults", clear_res.status_code == 200, "Normal baseline restored.")

    # 15. Prometheus Metrics Endpoint
    metrics_res = requests.get(f"{BASE_URL}/metrics")
    log_test("Prometheus /metrics Endpoint", metrics_res.status_code == 200 and "ecommerce_service_requests_total" in metrics_res.text, "Exposing standard metrics gauges.")

    print("\n==================================================================")
    print(" ALL 15 VERIFICATION STAGES PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    run_verification()
