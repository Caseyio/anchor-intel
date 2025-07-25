# scripts/create_admin_user.py

import sys
import os

# Add the /app directory to Python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal
from app.models.models import User
from app.auth.auth import get_password_hash


def create_admin_user():
    db = SessionLocal()
    username = "admin"
    password = "admin123"

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print("✅ Admin user already exists.")
        return

    hashed = get_password_hash(password)
    new_user = User(username=username, password_hash=hashed, role="admin")
    db.add(new_user)
    db.commit()
    print("✅ Admin user created with password:", password)


if __name__ == "__main__":
    create_admin_user()
