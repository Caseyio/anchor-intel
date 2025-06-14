# 📁 app/auth/auth.py

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 🔐 Config
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# 📌 Logger
logger = logging.getLogger(__name__)

# 🔑 Header extraction
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


# 🎟️ Token creation
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 👤 Current user dependency
async def get_current_user(token: Optional[str] = Depends(api_key_header)) -> Dict:
    if token is None or not token.startswith("Bearer "):
        logger.warning("Missing or invalid auth header")
        raise HTTPException(
            status_code=401, detail="Authorization header missing or invalid"
        )

    jwt_token = token.replace("Bearer ", "")
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"username": username, "role": role}
    except JWTError as e:
        logger.error(f"JWT decode failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Token validation failed")


# 🛡️ Role-based access dependency
def require_role(required_role: str):
    async def role_checker(user: Dict = Depends(get_current_user)):
        if user["role"] != required_role:
            logger.warning(
                f"Unauthorized access attempt by user "
                f"{user['username']} for role {required_role}"
            )
            raise HTTPException(status_code=403, detail="Not authorized")
        return user

    return role_checker
