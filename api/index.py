import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.common.database import Base, engine, SessionLocal
from services.common.models import ProductModel

# Initialize database schema in /tmp if on Vercel
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(ProductModel).count() == 0:
        from scripts.seed_data import seed
        seed()
    db.close()
except Exception as e:
    print(f"Database init / seed notice: {e}")

from services.api_gateway.main import app

app = app
