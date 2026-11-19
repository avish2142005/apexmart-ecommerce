import sys
import os

# Add root directory to sys.path so microservices packages resolve cleanly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_gateway.main import app

# Export FastAPI app for Vercel Serverless
app = app
