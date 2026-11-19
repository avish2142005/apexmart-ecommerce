import time
import random
import threading
from typing import Dict, Any, Optional, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

class FaultRule:
    def __init__(
        self,
        fault_id: str,
        target_service: str,
        fault_type: str,
        error_code: int = 500,
        error_message: str = "Simulated fault injected",
        delay_ms: int = 0,
        error_rate_pct: int = 100,
        duration_seconds: int = 60,
        scenario_name: Optional[str] = None
    ):
        self.fault_id = fault_id
        self.target_service = target_service  # e.g. "payment-service", "inventory-service", "all"
        self.fault_type = fault_type          # "latency", "http_error", "timeout", "db_error", "rabbitmq_error", "degradation"
        self.error_code = error_code
        self.error_message = error_message
        self.delay_ms = delay_ms
        self.error_rate_pct = error_rate_pct
        self.duration_seconds = duration_seconds
        self.start_time = time.time()
        self.scenario_name = scenario_name

    def is_active(self) -> bool:
        if self.duration_seconds > 0 and (time.time() - self.start_time > self.duration_seconds):
            return False
        return True

    def matches(self, service_name: str) -> bool:
        if not self.is_active():
            return False
        return self.target_service in ("all", service_name)

    def to_dict(self) -> Dict[str, Any]:
        elapsed = int(time.time() - self.start_time)
        remaining = max(0, self.duration_seconds - elapsed) if self.duration_seconds > 0 else -1
        return {
            "fault_id": self.fault_id,
            "target_service": self.target_service,
            "fault_type": self.fault_type,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "delay_ms": self.delay_ms,
            "error_rate_pct": self.error_rate_pct,
            "duration_seconds": self.duration_seconds,
            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,
            "active": self.is_active(),
            "scenario_name": self.scenario_name
        }


class FaultManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FaultManager, cls).__new__(cls)
                cls._instance._rules: Dict[str, FaultRule] = {}
        return cls._instance

    def add_rule(self, rule: FaultRule) -> FaultRule:
        with self._lock:
            self._rules[rule.fault_id] = rule
        return rule

    def remove_rule(self, fault_id: str) -> bool:
        with self._lock:
            if fault_id in self._rules:
                del self._rules[fault_id]
                return True
        return False

    def clear_all(self):
        with self._lock:
            self._rules.clear()

    def get_active_rules(self) -> List[Dict[str, Any]]:
        with self._lock:
            # prune expired
            active = []
            for r in list(self._rules.values()):
                if r.is_active():
                    active.append(r.to_dict())
            return active

    def check_and_apply(self, service_name: str, endpoint: str = ""):
        """Called inside middleware or endpoints. May sleep, raise HTTPException, or simulate DB/MQ error."""
        with self._lock:
            matching_rules = [r for r in self._rules.values() if r.matches(service_name)]

        for rule in matching_rules:
            # Check probability
            if random.randint(1, 100) > rule.error_rate_pct:
                continue

            # Handle Gradual Degradation: delay increases with elapsed time
            current_delay = rule.delay_ms
            if rule.fault_type == "degradation":
                elapsed = time.time() - rule.start_time
                # Gradual ramp-up: up to 5000ms delay as time passes
                current_delay = int(min(6000, 500 + elapsed * 100))

            if current_delay > 0:
                time.sleep(current_delay / 1000.0)

            # Check fault injection types
            if rule.fault_type in ("http_error", "degradation") and rule.error_code >= 400:
                # If degradation, only throw error once heavily delayed
                if rule.fault_type == "degradation" and random.random() < 0.3:
                    raise HTTPException(status_code=rule.error_code, detail=rule.error_message)
                elif rule.fault_type == "http_error":
                    raise HTTPException(status_code=rule.error_code, detail=rule.error_message)

            elif rule.fault_type == "timeout":
                time.sleep(rule.delay_ms / 1000.0 if rule.delay_ms > 0 else 5.0)
                raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Service timed out during processing")

            elif rule.fault_type == "db_error":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OperationalError: Database connection pool exhausted or dropped")

            elif rule.fault_type == "rabbitmq_error":
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AMQPConnectionError: RabbitMQ broker broker unreachable")

            elif rule.fault_type == "redis_error":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RedisConnectionError: Error connecting to Redis cache on 6379")

            elif rule.fault_type == "crash":
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Service {service_name} crashed: Connection reset by peer")

# Global singleton
fault_manager = FaultManager()
