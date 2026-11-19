import logging
import json
import datetime
import sys
from typing import Optional

class JSONFormatter(logging.Formatter):
    def __init__(self, service_name: str = "ecommerce-service"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": record.levelname,
            "service_name": self.service_name,
            "message": record.getMessage(),
            "module": record.module,
            "lineno": record.lineno,
        }

        # Enrich with context attributes if present
        for attr in ["correlation_id", "transaction_id", "trace_id", "span_id", "status_code", "duration_ms", "endpoint", "method"]:
            if hasattr(record, attr):
                log_obj[attr] = getattr(record, attr)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)

def get_logger(service_name: str) -> logging.Logger:
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter(service_name))
        logger.addHandler(handler)
        logger.propagate = False
        
    return logger
