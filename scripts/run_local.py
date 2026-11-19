import os
import sys
import uvicorn

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    port = int(os.getenv("GATEWAY_PORT", "8000"))
    print(f"================================================================")
    print(f" Starting E-Commerce Microservices Platform on http://127.0.0.1:{port}")
    print(f" Telemetry stream available at /api/telemetry/stream")
    print(f" Swagger UI docs available at http://127.0.0.1:{port}/docs")
    print(f"================================================================")
    uvicorn.run("services.api_gateway.main:app", host="0.0.0.0", port=port, reload=False, log_level="info")
