from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List

from app.db.database import database
from app.db.tables import products
from app.schemas.alerts import LowStockAlert
from app.utils.logger import logger

router = APIRouter()


# 5. Low stock alerts
@router.get("/alerts/low-stock", response_model=List[LowStockAlert])
async def low_stock_alerts(threshold: int = 10):
    try:
        logger.info(f"🔍 Checking for low-stock products (threshold ≤ {threshold})")

        query = products.select().where(products.c.stock_quantity <= threshold)
        rows = await database.fetch_all(query)

        logger.info(f"⚠️ Found {len(rows)} products at or below threshold")
        return rows

    except Exception as e:
        logger.error(f"🔥 Error retrieving low-stock alerts: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": "Failed to fetch low-stock products"}
        )
