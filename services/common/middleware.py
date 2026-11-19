import time
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from services.common.tracing import extract_tracing_context, inject_tracing_headers
from services.common.logger import get_logger
from services.common.fault_injection import fault_manager
from services.common.telemetry import telemetry_collector

class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name
        self.logger = get_logger(service_name)

    async def dispatch(self, request: Request, call_next):
        # Skip telemetry for internal metrics polling to avoid noise
        path = request.url.path
        is_internal = path in ("/metrics", "/health", "/favicon.ico")

        # 1. Tracing context
        ctx = extract_tracing_context(request)
        start_time = time.time()
        status_code = 500
        error_msg = None

        try:
            # 2. Check and apply active fault injection (unless it's health check)
            if not is_internal:
                fault_manager.check_and_apply(self.service_name, endpoint=path)

            # 3. Call downstream
            response = await call_next(request)
            status_code = response.status_code

        except HTTPException as he:
            status_code = he.status_code
            error_msg = str(he.detail)
            response = JSONResponse(
                status_code=he.status_code,
                content={"error": error_msg, "service": self.service_name, "status_code": he.status_code}
            )
        except Exception as ex:
            status_code = 500
            error_msg = str(ex)
            response = JSONResponse(
                status_code=500,
                content={"error": f"Internal Server Error: {str(ex)}", "service": self.service_name, "status_code": 500}
            )

        duration_ms = (time.time() - start_time) * 1000

        # 4. Inject tracing headers into response
        for k, v in inject_tracing_headers(ctx).items():
            response.headers[k] = v
        response.headers["x-response-time-ms"] = f"{duration_ms:.2f}"
        response.headers["x-service-name"] = self.service_name

        # 5. Record telemetry & log
        if not is_internal:
            telemetry_collector.record_request(
                service_name=self.service_name,
                endpoint=path,
                http_method=request.method,
                status_code=status_code,
                response_time_ms=duration_ms,
                correlation_id=ctx["correlation_id"],
                transaction_id=ctx["transaction_id"],
                error_message=error_msg
            )

            # Structured Log
            extra_dict = {
                "correlation_id": ctx["correlation_id"],
                "transaction_id": ctx["transaction_id"],
                "trace_id": ctx["trace_id"],
                "span_id": ctx["span_id"],
                "endpoint": path,
                "method": request.method,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2)
            }
            if status_code >= 500:
                self.logger.error(f"{request.method} {path} -> {status_code} ({duration_ms:.1f}ms): {error_msg}", extra=extra_dict)
            elif status_code >= 400:
                self.logger.warning(f"{request.method} {path} -> {status_code} ({duration_ms:.1f}ms)", extra=extra_dict)
            else:
                self.logger.info(f"{request.method} {path} -> {status_code} ({duration_ms:.1f}ms)", extra=extra_dict)

        return response


def setup_standard_routes(app: FastAPI, service_name: str):
    """Registers standard /health and /metrics endpoints on every microservice."""
    @app.get("/health", tags=["Health"])
    def health_check():
        return {
            "status": "UP",
            "service": service_name,
            "timestamp": time.time(),
        }

    @app.get("/metrics", tags=["Metrics"])
    def metrics():
        return PlainTextResponse(telemetry_collector.generate_prometheus_metrics())
