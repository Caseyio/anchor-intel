# routes/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth import create_access_token, verify_password
from app.db.database import get_db
from app.models.models import User, Tenant
from app.models.schemas import TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(User)
        .filter(User.username == form_data.username, User.tenant_id.isnot(None))
        .first()
    )

    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    tenant = db.query(Tenant).filter(Tenant.id == db_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant configuration error.")

    token = create_access_token(
        {
            "sub": db_user.username,
            "user_id": db_user.id,
            "tenant_id": str(db_user.tenant_id),
            "role": db_user.role,
            "tenant_name": tenant.name,
        }
    )

    return {"access_token": token, "token_type": "bearer"}
