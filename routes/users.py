from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.models import User
from app.models.schemas import UserCreate, UserOut, LoginInput, TokenResponse
from passlib.hash import bcrypt
from app.auth.auth import create_access_token, require_role, get_current_user
from app.db.database import get_db
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)


# 👤 Register a new user
@router.post("/users/register", response_model=UserOut)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    logger.info(
        f"📥 Registration attempt for username: {user.username} (role: {user.role}) by admin {current_user.username}"
    )

    try:
        existing_user = (
            db.query(User)
            .filter(
                User.username == user.username,
                User.tenant_id == current_user.tenant_id,
            )
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed_pw = bcrypt.hash(user.password)
        new_user = User(
            username=user.username,
            password_hash=hashed_pw,
            role=user.role,
            tenant_id=current_user.tenant_id,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(
            f"✅ User registered: {new_user.username} (ID: {new_user.id}, role: {new_user.role}, tenant: {new_user.tenant_id})"
        )
        return new_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Registration failed for {user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration error")


# 🔐 Login endpoint
@router.post("/login", response_model=TokenResponse)
def login(user: LoginInput, db: Session = Depends(get_db)):
    logger.info(f"🔐 Login attempt for username: {user.username}")

    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        logger.warning(f"⚠️ Login failed: User '{user.username}' not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.verify(user.password, db_user.password_hash):
        logger.warning(f"⚠️ Login failed: Incorrect password for user '{user.username}'")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={
            "sub": db_user.username,
            "role": db_user.role,
            "tenant_id": str(db_user.tenant_id),
        }
    )
    logger.info(
        f"✅ Login successful for user '{user.username}' with role '{db_user.role}' and tenant '{db_user.tenant_id}'"
    )
    return {"access_token": token, "token_type": "bearer"}


# 📋 List all users (admin only)
@router.get("/users", response_model=List[UserOut])
def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .filter(User.tenant_id == current_user.tenant_id)
        .order_by(User.id)
        .all()
    )
    return users


@router.get("/cashiers")
def get_cashiers(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    results = (
        db.query(User.id, User.username.label("name"))
        .filter(User.role == "cashier", User.tenant_id == current_user.tenant_id)
        .all()
    )
    return [{"id": r.id, "name": r.name} for r in results]
