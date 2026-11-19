import os

# Service Port Mapping
SERVICE_PORTS = {
    "auth-service": int(os.getenv("AUTH_SERVICE_PORT", "8001")),
    "catalog-service": int(os.getenv("CATALOG_SERVICE_PORT", "8002")),
    "search-service": int(os.getenv("SEARCH_SERVICE_PORT", "8003")),
    "inventory-service": int(os.getenv("INVENTORY_SERVICE_PORT", "8004")),
    "cart-service": int(os.getenv("CART_SERVICE_PORT", "8005")),
    "pricing-service": int(os.getenv("PRICING_SERVICE_PORT", "8006")),
    "checkout-service": int(os.getenv("CHECKOUT_SERVICE_PORT", "8007")),
    "payment-service": int(os.getenv("PAYMENT_SERVICE_PORT", "8008")),
    "order-service": int(os.getenv("ORDER_SERVICE_PORT", "8009")),
    "shipping-service": int(os.getenv("SHIPPING_SERVICE_PORT", "8010")),
    "notification-service": int(os.getenv("NOTIFICATION_SERVICE_PORT", "8011")),
    "support-service": int(os.getenv("SUPPORT_SERVICE_PORT", "8012")),
    "review-service": int(os.getenv("REVIEW_SERVICE_PORT", "8013")),
    "analytics-service": int(os.getenv("ANALYTICS_SERVICE_PORT", "8014")),
    "admin-service": int(os.getenv("ADMIN_SERVICE_PORT", "8015")),
    "api-gateway": int(os.getenv("GATEWAY_PORT", "8000")),
}

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-ecommerce-key-2026-production-ready")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_service_url(service_name: str) -> str:
    # If running inside docker compose network, resolve by service name
    docker_host = os.getenv(f"{service_name.upper().replace('-', '_')}_HOST")
    if docker_host:
        return f"http://{docker_host}:{SERVICE_PORTS[service_name]}"
    
    # In docker, use service container name
    if os.getenv("IN_DOCKER"):
        return f"http://{service_name}:{SERVICE_PORTS[service_name]}"
    
    # Localhost fallback
    return f"http://127.0.0.1:{SERVICE_PORTS[service_name]}"
