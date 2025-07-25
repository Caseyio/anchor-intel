import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.models.models import Base

# ─────────────────────────────
# Load environment variables
# ─────────────────────────────
load_dotenv()

# ─────────────────────────────
# Database Configuration
# ─────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://caseyortiz@localhost/liquor_store",  # fallback for local dev
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ─────────────────────────────
# Dependency Injection
# ─────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
