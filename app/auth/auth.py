# 📁 app/auth/auth.py

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User  # ORM User model
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────────
# 🔐 Config
# ─────────────────────────────────────────────
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# 🔌 Token extraction from Authorization header
api_key_header = APIKeyHeader(name="Authorization")

# 📌 Logger
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 🎟️ JWT Token creation
# ─────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ─────────────────────────────────────────────
# 👤 Current user dependency
# ─────────────────────────────────────────────
def get_current_user(
    token: str = Depends(api_key_header),
    db: Session = Depends(get_db),
) -> User:
    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )

    try:
        token_value = token.replace("Bearer ", "")
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError as e:
        logger.error(f"JWT decode failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Token validation failed")


# ─────────────────────────────────────────────
# 🛡️ Role-based access checker
# ─────────────────────────────────────────────
def require_role(required_role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            logger.warning(
                f"Unauthorized access: user '{user.username}' attempted '{required_role}' access"
            )
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return user

    return role_checker
