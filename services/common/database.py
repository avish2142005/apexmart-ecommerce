import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    # Use SQLite file in local data dir as default zero-config fallback
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    source_db = os.path.join(DATA_DIR, "ecommerce.db")

    if os.getenv("VERCEL"):
        tmp_db = "/tmp/ecommerce.db"
        if not os.path.exists(tmp_db) and os.path.exists(source_db):
            try:
                shutil.copyfile(source_db, tmp_db)
            except Exception:
                pass
        target_db = tmp_db if os.path.exists(tmp_db) else source_db
        DATABASE_URL = f"sqlite:///{target_db}"
    else:
        os.makedirs(DATA_DIR, exist_ok=True)
        DATABASE_URL = f"sqlite:///{source_db}"

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
