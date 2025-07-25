# routes/alerts.py

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import Product, User
from schemas.alerts import LowStockAlert
from app.core.logging_config import logger
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/low-stock", response_model=List[LowStockAlert])
def low_stock_alerts(
    threshold: int = Query(10, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        logger.info(
            f"🔍 Checking low-stock products (threshold ≤ {threshold}) for tenant '{current_user.tenant_id}'"
        )

        low_stock_products = (
            db.query(Product)
            .filter(
                Product.stock_quantity <= threshold,
                Product.tenant_id == current_user.tenant_id,
            )
            .all()
        )

        logger.info(
            f"⚠️ Found {len(low_stock_products)} products at or below threshold for tenant '{current_user.tenant_id}'"
        )

        alerts = [
            LowStockAlert(
                product_id=product.id,
                name=product.name,
                stock_level=product.stock_quantity,
            )
            for product in low_stock_products
        ]

        return alerts

    except Exception as e:
        logger.error(f"🔥 Error retrieving low-stock alerts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to fetch low-stock products"
        )
