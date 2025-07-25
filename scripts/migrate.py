# scripts/migrate.py

from app.db.database import engine
from app.models.models import Base  # <-- ORM Base class

Base.metadata.create_all(bind=engine)
print("✅ ORM tables created")
