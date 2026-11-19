import os
import shutil
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    source_db = os.path.join(DATA_DIR, "ecommerce.db")

    if os.getenv("VERCEL"):
        tmp_db = "/tmp/ecommerce.db"
        if not os.path.exists(tmp_db) and os.path.exists(source_db):
            try:
                shutil.copyfile(source_db, tmp_db)
            except Exception:
                pass
        DATABASE_URL = f"sqlite:///{tmp_db}"
    else:
        os.makedirs(DATA_DIR, exist_ok=True)
        DATABASE_URL = f"sqlite:///{source_db}"

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def apply_database_migrations():
    """Ensures user and table schema columns are up to date."""
    try:
        with engine.connect() as conn:
            # Check SQLite table info for users
            if "sqlite" in DATABASE_URL:
                res = conn.execute(text("PRAGMA table_info(users)"))
                cols = [r[1] for r in res.fetchall()]
                if cols:
                    if "is_active" not in cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                    if "failed_login_attempts" not in cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"))
                    if "last_login" not in cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
                    conn.commit()
    except Exception as e:
        # Tables might not be created yet; create_all will create them with latest schema
        pass

# Run migrations if database is already present
apply_database_migrations()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
