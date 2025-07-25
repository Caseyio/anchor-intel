# routes/cashier_session.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from app.models.models import CashierSession, Sale, User
from app.models.schemas import (
    CashierSessionCreate,
    CashierSessionClose,
    CashierSessionOut,
)
from app.db.database import get_db
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/cashier_sessions", tags=["Cashier Sessions"])


@router.post("/open", response_model=CashierSessionOut)
def open_session(
    session_data: CashierSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    open_session = (
        db.query(CashierSession)
        .filter(
            CashierSession.cashier_id == current_user.id,
            CashierSession.closed_at.is_(None),
            CashierSession.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if open_session:
        raise HTTPException(
            status_code=400, detail="Cashier already has an open session."
        )

    session = CashierSession(
        cashier_id=current_user.id,
        tenant_id=current_user.tenant_id,
        terminal_id=session_data.terminal_id,
        opened_at=datetime.utcnow(),
        opening_cash=session_data.opening_cash,
        notes=session_data.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/{session_id}/close", response_model=CashierSessionOut)
def close_session(
    session_id: int,
    close_data: CashierSessionClose,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(CashierSession)
        .filter(
            CashierSession.id == session_id,
            CashierSession.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.cashier_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if session.closed_at:
        raise HTTPException(status_code=400, detail="Session already closed.")

    sales = (
        db.query(Sale)
        .filter(
            Sale.timestamp >= session.opened_at,
            Sale.timestamp <= datetime.utcnow(),
            Sale.payment_type == "cash",
            Sale.cashier_id == current_user.id,
            Sale.tenant_id == current_user.tenant_id,
        )
        .all()
    )
    system_total = sum([s.total_amount for s in sales])
    difference = close_data.closing_cash - system_total

    session.closing_cash = close_data.closing_cash
    session.system_cash_total = system_total
    session.cash_difference = difference
    session.is_over_short = difference != Decimal("0.00")
    session.closed_at = datetime.utcnow()
    session.notes = close_data.notes

    db.commit()
    db.refresh(session)
    return session


@router.get("/current", response_model=CashierSessionOut)
def get_current_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(CashierSession)
        .filter(
            CashierSession.cashier_id == current_user.id,
            CashierSession.closed_at.is_(None),
            CashierSession.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="No active session.")
    return session


@router.get("/{session_id}/summary")
def get_session_summary(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(CashierSession)
        .filter(
            CashierSession.id == session_id,
            CashierSession.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.cashier_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized.")

    sales = (
        db.query(Sale)
        .filter(
            Sale.timestamp >= session.opened_at,
            Sale.payment_type == "cash",
            Sale.cashier_id == current_user.id,
            Sale.tenant_id == current_user.tenant_id,
        )
        .all()
    )
    system_total = sum([s.total_amount for s in sales])
    return {"session_id": session.id, "system_cash_total": float(system_total)}
