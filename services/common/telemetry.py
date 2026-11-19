import time
import datetime
import psutil
import threading
from typing import Dict, Any, List, Optional
from collections import deque

class TelemetryCollector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TelemetryCollector, cls).__new__(cls)
                cls._instance._telemetry_records = deque(maxlen=2000)
                cls._instance._service_stats = {}
                cls._instance._service_dependencies = {
                    "checkout-service": ["cart-service", "inventory-service", "pricing-service", "order-service", "payment-service"],
                    "order-service": ["payment-service", "inventory-service", "shipping-service", "notification-service"],
                    "payment-service": ["notification-service"],
                    "shipping-service": ["notification-service"],
                    "cart-service": ["catalog-service", "inventory-service"],
                    "search-service": ["catalog-service"],
                    "admin-service": ["catalog-service", "order-service", "inventory-service", "analytics-service"],
                }
        return cls._instance

    def record_request(
        self,
        service_name: str,
        endpoint: str,
        http_method: str,
        status_code: int,
        response_time_ms: float,
        correlation_id: str,
        transaction_id: str,
        error_message: Optional[str] = None
    ):
        # Determine severity
        severity = "INFO"
        if status_code >= 500 or response_time_ms > 3000:
            severity = "HIGH"
        elif status_code >= 400 or response_time_ms > 1000:
            severity = "MEDIUM"

        record = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "service_name": service_name,
            "endpoint": endpoint,
            "http_method": http_method,
            "status_code": status_code,
            "response_time_ms": round(response_time_ms, 2),
            "error_message": error_message or ("" if status_code < 400 else f"HTTP {status_code} Error"),
            "correlation_id": correlation_id,
            "transaction_id": transaction_id,
            "severity": severity
        }

        with self._lock:
            self._telemetry_records.append(record)

            # Update aggregated service stats
            if service_name not in self._service_stats:
                self._service_stats[service_name] = {
                    "total_requests": 0,
                    "failed_requests": 0,
                    "latencies": deque(maxlen=200),
                    "last_seen": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "cpu_percent": 0.0,
                    "memory_mb": 0.0
                }

            stat = self._service_stats[service_name]
            stat["total_requests"] += 1
            if status_code >= 400:
                stat["failed_requests"] += 1
            stat["latencies"].append(response_time_ms)
            stat["last_seen"] = record["timestamp"]

    def get_service_health(self) -> Dict[str, Any]:
        """Provides status of every microservice for RootGuard and dashboard."""
        all_services = [
            "auth-service", "catalog-service", "search-service", "inventory-service",
            "cart-service", "pricing-service", "checkout-service", "payment-service",
            "order-service", "shipping-service", "notification-service", "support-service",
            "review-service", "analytics-service", "admin-service", "api-gateway"
        ]

        # Sample system metrics
        cpu_usage = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()

        health_map = {}
        with self._lock:
            for s_name in all_services:
                stat = self._service_stats.get(s_name, {
                    "total_requests": 0,
                    "failed_requests": 0,
                    "latencies": [],
                    "last_seen": None,
                })
                total = stat["total_requests"]
                failed = stat["failed_requests"]
                error_rate = round((failed / total * 100), 1) if total > 0 else 0.0
                latencies = list(stat.get("latencies", []))
                avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 12.5

                status_label = "HEALTHY"
                if error_rate > 20 or avg_latency > 2500:
                    status_label = "CRITICAL"
                elif error_rate > 5 or avg_latency > 800:
                    status_label = "DEGRADED"

                health_map[s_name] = {
                    "service_name": s_name,
                    "status": status_label,
                    "error_rate_pct": error_rate,
                    "avg_latency_ms": avg_latency,
                    "total_requests": total,
                    "failed_requests": failed,
                    "last_seen": stat.get("last_seen"),
                    "dependencies": self._service_dependencies.get(s_name, [])
                }

        return {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "system_cpu_percent": cpu_usage,
            "system_memory_used_mb": round(mem.used / (1024 * 1024), 1),
            "system_memory_percent": mem.percent,
            "services": health_map
        }

    def get_telemetry_logs(self, limit: int = 100, service: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            logs = list(self._telemetry_records)

        if service:
            logs = [l for l in logs if l["service_name"] == service]
        if severity:
            logs = [l for l in logs if l["severity"] == severity]

        return list(reversed(logs[-limit:]))

    def generate_prometheus_metrics(self) -> str:
        """Prometheus metrics exposition format."""
        health = self.get_service_health()
        lines = [
            "# HELP ecommerce_service_requests_total Total HTTP requests handled",
            "# TYPE ecommerce_service_requests_total counter",
        ]
        for s_name, s_info in health["services"].items():
            lines.append(f'ecommerce_service_requests_total{{service="{s_name}"}} {s_info["total_requests"]}')

        lines.extend([
            "# HELP ecommerce_service_failures_total Total failed requests (status >= 400)",
            "# TYPE ecommerce_service_failures_total counter",
        ])
        for s_name, s_info in health["services"].items():
            lines.append(f'ecommerce_service_failures_total{{service="{s_name}"}} {s_info["failed_requests"]}')

        lines.extend([
            "# HELP ecommerce_service_latency_ms Average service response latency in milliseconds",
            "# TYPE ecommerce_service_latency_ms gauge",
        ])
        for s_name, s_info in health["services"].items():
            lines.append(f'ecommerce_service_latency_ms{{service="{s_name}"}} {s_info["avg_latency_ms"]}')

        lines.extend([
            "# HELP system_cpu_utilization Current system CPU utilization percent",
            "# TYPE system_cpu_utilization gauge",
            f'system_cpu_utilization {health["system_cpu_percent"]}',
            "# HELP system_memory_usage_mb System memory used in MB",
            "# TYPE system_memory_usage_mb gauge",
            f'system_memory_usage_mb {health["system_memory_used_mb"]}',
        ])
        return "\n".join(lines) + "\n"

telemetry_collector = TelemetryCollector()
