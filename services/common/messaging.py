import os
import json
import uuid
import datetime
import threading
import logging
from typing import Dict, Any, Callable, List, Optional
from services.common.config import RABBITMQ_URL, RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS
from services.common.fault_injection import fault_manager

logger = logging.getLogger("messaging")

class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._subscribers = {}
                cls._instance._event_history = []
                cls._instance._pika_available = False
                cls._instance._channel = None
                cls._instance._init_rabbitmq()
        return cls._instance

    def _init_rabbitmq(self):
        try:
            import pika
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
                connection_attempts=1,
                retry_delay=1,
                socket_timeout=2
            )
            connection = pika.BlockingConnection(parameters)
            self._channel = connection.channel()
            self._channel.exchange_declare(exchange="ecommerce_events", exchange_type="topic", durable=True)
            self._pika_available = True
            logger.info("Connected to RabbitMQ broker successfully.")
        except Exception as e:
            self._pika_available = False
            logger.warning(f"RabbitMQ broker not reachable ({e}). Using in-memory event bus with full telemetry.")

    def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source_service: str,
        correlation_id: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Check fault injection for rabbitmq failure
        fault_manager.check_and_apply(source_service, endpoint="rabbitmq_publish")

        event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_service": source_service,
            "correlation_id": correlation_id or f"COR-{uuid.uuid4().hex[:8].upper()}",
            "transaction_id": transaction_id or f"TXN-{uuid.uuid4().hex[:8].upper()}",
            "payload": payload
        }

        # Store in event history (capped at 500 events for RootGuard telemetry)
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > 500:
                self._event_history.pop(0)

        # Dispatch via RabbitMQ if active
        if self._pika_available and self._channel:
            try:
                import pika
                self._channel.basic_publish(
                    exchange="ecommerce_events",
                    routing_key=event_type,
                    body=json.dumps(event),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        correlation_id=event["correlation_id"],
                        content_type="application/json"
                    )
                )
            except Exception as ex:
                logger.error(f"Error publishing to RabbitMQ: {ex}")
                self._pika_available = False

        # In-memory distribution to local subscribers
        handlers = self._subscribers.get(event_type, []) + self._subscribers.get("*", [])
        for handler in handlers:
            try:
                threading.Thread(target=handler, args=(event,), daemon=True).start()
            except Exception as exc:
                logger.error(f"Error executing event subscriber for {event_type}: {exc}")

        return event

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return list(reversed(self._event_history[-limit:]))

event_bus = EventBus()
