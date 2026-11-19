import asyncio
import os
import json
import time
import uuid
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, Response, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel
import httpx

from services.common.config import SERVICE_PORTS, get_service_url
from services.common.tracing import extract_tracing_context, inject_tracing_headers
from services.common.fault_injection import fault_manager, FaultRule
from services.common.telemetry import telemetry_collector
from services.common.messaging import event_bus
from services.common.logger import get_logger

logger = get_logger("api-gateway")

app = FastAPI(
    title="E-Commerce API Gateway",
    version="1.0.0",
    description="Unified API Gateway routing requests to 15 microservices with OpenTelemetry tracing, Prometheus metrics, and fault simulation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------
# ROUTING MAP
# -----------------------------------------------------------------
SERVICE_ROUTE_MAP = {
    "auth": "auth-service",
    "catalog": "catalog-service",
    "search": "search-service",
    "inventory": "inventory-service",
    "cart": "cart-service",
    "pricing": "pricing-service",
    "checkout": "checkout-service",
    "payments": "payment-service",
    "orders": "order-service",
    "shipping": "shipping-service",
    "notifications": "notification-service",
    "support": "support-service",
    "reviews": "review-service",
    "analytics": "analytics-service",
    "admin": "admin-service"
}

# HTTP Client for proxying
http_client = httpx.AsyncClient(timeout=10.0)

# -----------------------------------------------------------------
# FAULT INJECTION CONTROLLER
# -----------------------------------------------------------------
class InjectFaultRequest(BaseModel):
    target_service: str
    fault_type: str # latency, http_error, timeout, db_error, rabbitmq_error, degradation
    error_code: Optional[int] = 500
    error_message: Optional[str] = "Injected synthetic failure"
    delay_ms: Optional[int] = 0
    error_rate_pct: Optional[int] = 100
    duration_seconds: Optional[int] = 60
    scenario_name: Optional[str] = None

@app.post("/api/v1/faults/inject")
def inject_fault(req: InjectFaultRequest):
    rule = FaultRule(
        fault_id=f"FLT-{uuid.uuid4().hex[:6].upper()}",
        target_service=req.target_service,
        fault_type=req.fault_type,
        error_code=req.error_code or 500,
        error_message=req.error_message or "Injected synthetic failure",
        delay_ms=req.delay_ms or 0,
        error_rate_pct=req.error_rate_pct or 100,
        duration_seconds=req.duration_seconds or 60,
        scenario_name=req.scenario_name
    )
    fault_manager.add_rule(rule)
    return {"message": f"Fault successfully injected into {req.target_service}", "rule": rule.to_dict()}

@app.get("/api/v1/faults/active")
def get_active_faults():
    return fault_manager.get_active_rules()

@app.delete("/api/v1/faults/clear-all")
def clear_all_faults():
    fault_manager.clear_all()
    return {"message": "All injected faults cleared."}

@app.delete("/api/v1/faults/{fault_id}")
def delete_fault(fault_id: str):
    removed = fault_manager.remove_rule(fault_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Fault rule not found")
    return {"message": f"Fault rule {fault_id} removed"}

@app.post("/api/v1/faults/scenario/{scenario_id}")
def trigger_predefined_scenario(scenario_id: int):
    """
    Triggers predefined real-world failure scenarios 1 through 6:
    1: PAYMENT FAILURE (Payment service timeout, payment fails, checkout fails)
    2: INVENTORY DEGRADATION (Inventory service response time gradually increases)
    3: DATABASE FAILURE (Product database unavailable, HTTP 500 on catalog/search)
    4: RABBITMQ FAILURE (Order events cannot be published, shipping not notified)
    5: SHIPPING SERVICE FAILURE (Shipping service unavailable, orders stuck)
    6: CASCADING FAILURE (Payment latency increases -> checkout times out -> orders delayed)
    """
    fault_manager.clear_all()

    if scenario_id == 1:
        # SCENARIO 1: PAYMENT FAILURE
        r = FaultRule(
            fault_id="SCENARIO-1-PAYMENT",
            target_service="payment-service",
            fault_type="timeout",
            delay_ms=4500,
            error_rate_pct=100,
            duration_seconds=120,
            scenario_name="Scenario 1: Payment Gateway Timeout & Decline"
        )
        fault_manager.add_rule(r)
        return {"scenario": 1, "name": "Payment Gateway Failure", "active_rules": [r.to_dict()]}

    elif scenario_id == 2:
        # SCENARIO 2: INVENTORY SERVICE DEGRADATION
        r = FaultRule(
            fault_id="SCENARIO-2-INVENTORY",
            target_service="inventory-service",
            fault_type="degradation",
            delay_ms=2500,
            error_rate_pct=80,
            duration_seconds=120,
            scenario_name="Scenario 2: Inventory Service Degradation"
        )
        fault_manager.add_rule(r)
        return {"scenario": 2, "name": "Inventory Service Degradation", "active_rules": [r.to_dict()]}

    elif scenario_id == 3:
        # SCENARIO 3: DATABASE FAILURE
        r = FaultRule(
            fault_id="SCENARIO-3-DATABASE",
            target_service="catalog-service",
            fault_type="db_error",
            error_code=500,
            error_message="OperationalError: Database connection pool exhausted or dropped",
            error_rate_pct=100,
            duration_seconds=90,
            scenario_name="Scenario 3: Product Catalog Database Failure"
        )
        fault_manager.add_rule(r)
        return {"scenario": 3, "name": "Catalog Database Failure", "active_rules": [r.to_dict()]}

    elif scenario_id == 4:
        # SCENARIO 4: RABBITMQ FAILURE
        r = FaultRule(
            fault_id="SCENARIO-4-RABBITMQ",
            target_service="order-service",
            fault_type="rabbitmq_error",
            error_code=503,
            error_message="AMQPConnectionError: RabbitMQ broker unreachable",
            error_rate_pct=100,
            duration_seconds=90,
            scenario_name="Scenario 4: RabbitMQ Broker Outage"
        )
        fault_manager.add_rule(r)
        return {"scenario": 4, "name": "RabbitMQ Outage", "active_rules": [r.to_dict()]}

    elif scenario_id == 5:
        # SCENARIO 5: SHIPPING SERVICE FAILURE
        r = FaultRule(
            fault_id="SCENARIO-5-SHIPPING",
            target_service="shipping-service",
            fault_type="http_error",
            error_code=503,
            error_message="Shipping Carrier API Unavailable: 503 Service Unavailable",
            error_rate_pct=100,
            duration_seconds=120,
            scenario_name="Scenario 5: Shipping Service Failure"
        )
        fault_manager.add_rule(r)
        return {"scenario": 5, "name": "Shipping Service Failure", "active_rules": [r.to_dict()]}

    elif scenario_id == 6:
        # SCENARIO 6: CASCADING FAILURE
        r1 = FaultRule(
            fault_id="SCENARIO-6-PAYMENT",
            target_service="payment-service",
            fault_type="latency",
            delay_ms=3500,
            error_rate_pct=90,
            duration_seconds=120,
            scenario_name="Scenario 6: Cascading Latency Spike"
        )
        r2 = FaultRule(
            fault_id="SCENARIO-6-CHECKOUT",
            target_service="checkout-service",
            fault_type="timeout",
            delay_ms=4000,
            error_rate_pct=75,
            duration_seconds=120,
            scenario_name="Scenario 6: Cascading Timeout"
        )
        fault_manager.add_rule(r1)
        fault_manager.add_rule(r2)
        return {"scenario": 6, "name": "Cascading Latency & Timeout Failure", "active_rules": [r1.to_dict(), r2.to_dict()]}

    else:
        raise HTTPException(status_code=400, detail="Scenario ID must be between 1 and 6")


# -----------------------------------------------------------------
# OBSERVABILITY & CENTRALIZED TELEMETRY ENDPOINTS
# -----------------------------------------------------------------
@app.get("/api/telemetry/services-health")
def get_services_health():
    """Returns real-time health, error rates, and latencies across all 15 microservices."""
    return telemetry_collector.get_service_health()

@app.get("/api/telemetry/logs")
def get_telemetry_logs(
    limit: int = Query(50, ge=1, le=500),
    service: Optional[str] = None,
    severity: Optional[str] = None
):
    """Centralized log and telemetry stream query endpoint."""
    return telemetry_collector.get_telemetry_logs(limit=limit, service=service, severity=severity)

@app.get("/api/telemetry/events")
def get_recent_events(limit: int = 50):
    """Returns recent RabbitMQ / Event Bus asynchronous messages."""
    return event_bus.get_recent_events(limit=limit)

@app.get("/api/telemetry/stream")
async def stream_telemetry():
    """Server-Sent Events (SSE) stream for live dashboard monitoring."""
    async def event_generator():
        while True:
            health = telemetry_collector.get_service_health()
            recent_logs = telemetry_collector.get_telemetry_logs(limit=5)
            active_faults = fault_manager.get_active_rules()

            data = json.dumps({
                "timestamp": time.time(),
                "health": health,
                "recent_logs": recent_logs,
                "active_faults": active_faults
            })
            yield f"data: {data}\n\n"
            await asyncio.sleep(2.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return PlainTextResponse(telemetry_collector.generate_prometheus_metrics())

@app.get("/health")
def gateway_health():
    return {"status": "UP", "service": "api-gateway", "timestamp": time.time()}


# -----------------------------------------------------------------
# UNIFIED LOCAL MODE / HTTP PROXY ROUTING
# -----------------------------------------------------------------
# If UNIFIED_MODE is true (default for local runs), mount all service apps directly
UNIFIED_MODE = os.getenv("UNIFIED_MODE", "true").lower() in ("true", "1", "yes")

if UNIFIED_MODE:
    try:
        from services.auth_service.main import app as auth_app
        from services.catalog_service.main import app as catalog_app
        from services.search_service.main import app as search_app
        from services.inventory_service.main import app as inventory_app
        from services.cart_service.main import app as cart_app
        from services.pricing_service.main import app as pricing_app
        from services.checkout_service.main import app as checkout_app
        from services.payment_service.main import app as payment_app
        from services.order_service.main import app as order_app
        from services.shipping_service.main import app as shipping_app
        from services.notification_service.main import app as notification_app
        from services.support_service.main import app as support_app
        from services.review_service.main import app as review_app
        from services.analytics_service.main import app as analytics_app
        from services.admin_service.main import app as admin_app

        app.mount("/api/v1/auth", auth_app)
        app.mount("/api/v1/catalog", catalog_app)
        app.mount("/api/v1/search", search_app)
        app.mount("/api/v1/inventory", inventory_app)
        app.mount("/api/v1/cart", cart_app)
        app.mount("/api/v1/pricing", pricing_app)
        app.mount("/api/v1/checkout", checkout_app)
        app.mount("/api/v1/payments", payment_app)
        app.mount("/api/v1/orders", order_app)
        app.mount("/api/v1/shipping", shipping_app)
        app.mount("/api/v1/notifications", notification_app)
        app.mount("/api/v1/support", support_app)
        app.mount("/api/v1/reviews", review_app)
        app.mount("/api/v1/analytics", analytics_app)
        app.mount("/api/v1/admin", admin_app)
        logger.info("Gateway initialized in UNIFIED MICROSERVICES mode (Direct fast routing).")
    except Exception as e:
        logger.warning(f"Could not mount unified apps directly ({e}). Falling back to HTTP proxy mode.")
        UNIFIED_MODE = False

# Reverse proxy fallback for Dockerized or multi-process mode
if not UNIFIED_MODE:
    @app.api_route("/api/v1/{service_key}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def route_service_request(service_key: str, path: str, request: Request):
        if service_key not in SERVICE_ROUTE_MAP:
            raise HTTPException(status_code=404, detail=f"Service route '/api/v1/{service_key}' not found on gateway")

        target_service = SERVICE_ROUTE_MAP[service_key]
        base_url = get_service_url(target_service)
        target_url = f"{base_url}/{path}" if path else base_url

        query_string = request.url.query
        if query_string:
            target_url = f"{target_url}?{query_string}"

        ctx = extract_tracing_context(request)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        headers = inject_tracing_headers(ctx, headers)

        body = await request.body()
        start_time = time.time()

        try:
            fault_manager.check_and_apply("api-gateway", endpoint=f"/api/v1/{service_key}/{path}")
            response = await http_client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body
            )
            duration_ms = (time.time() - start_time) * 1000
            res_headers = dict(response.headers)
            res_headers["x-correlation-id"] = ctx["correlation_id"]
            res_headers["x-transaction-id"] = ctx["transaction_id"]
            res_headers["x-response-time-ms"] = f"{duration_ms:.2f}"
            res_headers["x-proxied-service"] = target_service

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=res_headers,
                media_type=response.headers.get("content-type")
            )
        except Exception as ex:
            duration_ms = (time.time() - start_time) * 1000
            return JSONResponse(status_code=502, content={"error": f"Gateway Error: {str(ex)}", "service": target_service})
