from fastapi import APIRouter, Depends, HTTPException
from schemas import UserCreate, UserOut, LoginInput, TokenResponse
from app.database import database
from tables import users
from passlib.hash import bcrypt
from app.auth.auth import create_access_token, require_role
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# users
@router.post("/users/register", response_model=UserOut)
async def register_user(user: UserCreate):
    logger.info(
        f"📥 Registration attempt for username: {user.username} (role: {user.role})"
    )
    hashed_pw = bcrypt.hash(user.password)
    try:
        query = users.insert().values(
            username=user.username, password_hash=hashed_pw, role=user.role
        )
        user_id = await database.execute(query)
        logger.info(
            f"✅ User registered: {user.username} (ID: {user_id}, role: {user.role})"
        )
        return UserOut(id=user_id, username=user.username, role=user.role)
    except Exception as e:
        logger.error(f"❌ Registration failed for {user.username}: {str(e)}")
        raise HTTPException(status_code=400, detail="Username already exists")


@router.post("/login", response_model=TokenResponse)
async def login(user: LoginInput):
    logger.info(f"🔐 Login attempt for username: {user.username}")
    query = users.select().where(users.c.username == user.username)
    db_user = await database.fetch_one(query)

    if not db_user:
        logger.warning(f"⚠️ Login failed: User '{user.username}' not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.verify(user.password, db_user["password_hash"]):
        logger.warning(f"⚠️ Login failed: Incorrect password for user '{user.username}'")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": db_user["username"], "role": db_user["role"]}
    )
    logger.info(
        f"✅ Login successful for user '{user.username}' with role '{db_user['role']}'"
    )

    return {"access_token": token, "token_type": "bearer"}


# 👤 User management
@router.get("/users")
async def list_users(user: dict = Depends(require_role("admin"))):
    logger.info(f"📋 Admin '{user['username']}' requested user list")

    query = users.select()
    result = await database.fetch_all(query)

    logger.info(f"✅ Returned {len(result)} users to admin '{user['username']}'")
    return [
        {"id": u["id"], "username": u["username"], "role": u["role"]} for u in result
    ]
