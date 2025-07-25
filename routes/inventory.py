# routes/inventory.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.models import Product, InventoryEvent, User
from app.models.schemas import InventoryEventIn, InventoryEventOut
from app.auth.dependencies import get_current_user, require_role
from app.core.logging_config import logger

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# 📦 Create inventory event (admin only)
@router.post("/inventory-events", response_model=InventoryEventOut)
def create_inventory_event(
    event: InventoryEventIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    logger.info(
        f"📦 Inventory event request by admin: {user.username} "
        f"for product ID {event.product_id}, tenant {user.tenant_id}"
    )

    try:
        if event.change == 0:
            logger.warning("⚠️ Attempted to submit inventory event with change=0")
            raise HTTPException(
                status_code=400, detail="Inventory change cannot be zero"
            )

        product = (
            db.query(Product)
            .filter(
                Product.id == event.product_id,
                Product.tenant_id == user.tenant_id,
            )
            .first()
        )

        if not product:
            logger.warning(
                f"❌ Product ID {event.product_id} not found for tenant {user.tenant_id}"
            )
            raise HTTPException(status_code=404, detail="Product not found")

        # Update product quantity
        product.stock_quantity += event.change

        # Create inventory event
        now = datetime.utcnow()
        event_record = InventoryEvent(
            product_id=event.product_id,
            change=event.change,
            reason=event.reason,
            created_at=now,
            updated_at=now,
            tenant_id=user.tenant_id,
        )

        db.add_all([product, event_record])
        db.commit()
        db.refresh(event_record)

        logger.info(
            f"✅ Inventory event recorded for product {event.product_id}, tenant {user.tenant_id}: "
            f"change={event.change}, reason={event.reason}"
        )
        return event_record

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"🔥 Failed to create inventory event for product {event.product_id}, tenant {user.tenant_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Unexpected server error")


# 📦 List inventory events (admin only)
@router.get("/inventory-events", response_model=List[InventoryEventOut])
def list_inventory_events(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    try:
        logger.info(
            f"📦 Admin {user.username} requested inventory event history for tenant {user.tenant_id}"
        )

        results = (
            db.query(InventoryEvent)
            .join(Product, InventoryEvent.product_id == Product.id)
            .filter(Product.tenant_id == user.tenant_id)
            .order_by(InventoryEvent.created_at.desc())
            .all()
        )

        logger.info(
            f"✅ Returned {len(results)} inventory events to {user.username}, tenant {user.tenant_id}"
        )
        return results

    except Exception as e:
        logger.error(
            f"🔥 Error retrieving inventory events for tenant {user.tenant_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Unexpected server error")
