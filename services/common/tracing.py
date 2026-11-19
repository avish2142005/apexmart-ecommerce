import uuid
import time
from typing import Optional, Dict
from fastapi import Request

CORRELATION_ID_HEADER = "x-correlation-id"
TRANSACTION_ID_HEADER = "x-transaction-id"
TRACEPARENT_HEADER = "traceparent"

def generate_correlation_id() -> str:
    return f"COR-{uuid.uuid4().hex[:8].upper()}"

def generate_transaction_id() -> str:
    return f"TXN-{uuid.uuid4().hex[:8].upper()}"

def generate_trace_id() -> str:
    return uuid.uuid4().hex

def generate_span_id() -> str:
    return uuid.uuid4().hex[:16]

def extract_tracing_context(request: Request) -> Dict[str, str]:
    headers = request.headers
    
    # Traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
    traceparent = headers.get(TRACEPARENT_HEADER)
    if traceparent and len(traceparent.split("-")) >= 4:
        parts = traceparent.split("-")
        trace_id = parts[1]
        parent_span_id = parts[2]
    else:
        trace_id = generate_trace_id()
        parent_span_id = None

    span_id = generate_span_id()
    correlation_id = headers.get(CORRELATION_ID_HEADER) or generate_correlation_id()
    transaction_id = headers.get(TRANSACTION_ID_HEADER) or generate_transaction_id()

    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "correlation_id": correlation_id,
        "transaction_id": transaction_id,
        "traceparent": f"00-{trace_id}-{span_id}-01",
    }

def inject_tracing_headers(context: Dict[str, str], headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    out = dict(headers or {})
    out[CORRELATION_ID_HEADER] = context.get("correlation_id", generate_correlation_id())
    out[TRANSACTION_ID_HEADER] = context.get("transaction_id", generate_transaction_id())
    out[TRACEPARENT_HEADER] = context.get("traceparent", f"00-{generate_trace_id()}-{generate_span_id()}-01")
    return out
