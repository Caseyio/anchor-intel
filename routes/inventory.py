from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime

from app.db.database import database
from app.db.tables import products, inventory_events
from app.schemas import InventoryEventIn, InventoryEventOut
from app.auth.dependencies import get_current_user, require_role
from app.core.logging_config import logger

app = APIRouter()


# 📦 Inventory tracking
@app.post("/inventory-events", response_model=InventoryEventOut)
async def create_inventory_event(
    event: InventoryEventIn, user: dict = Depends(require_role("admin"))
):
    logger.info(
        f"📦 Inventory event request by admin: {user['username']} "
        f"for product ID {event.product_id}"
    )

    try:
        # Confirm product exists
        query = products.select().where(products.c.id == event.product_id)
        product = await database.fetch_one(query)

        if not product:
            logger.warning(
                f"❌ Product ID {event.product_id} not found for "
                f"inventory adjustment"
            )
            raise HTTPException(status_code=404, detail="Product not found")

        # Update inventory
        new_stock = product["stock_quantity"] + event.change
        await database.execute(
            products.update()
            .where(products.c.id == event.product_id)
            .values(stock_quantity=new_stock)
        )

        # Log event
        insert_query = inventory_events.insert().values(
            product_id=event.product_id,
            change=event.change,
            reason=event.reason,
            created_at=datetime.utcnow(),
        )
        event_id = await database.execute(insert_query)

        logger.info(
            f"✅ Inventory event recorded for product {event.product_id}: "
            f"change={event.change}, reason={event.reason}"
        )
        return {**event.dict(), "id": event_id, "created_at": datetime.utcnow()}

    except Exception as e:
        logger.error(
            f"🔥 Failed to create inventory event for product "
            f"{event.product_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Unexpected server error")


@app.get("/inventory-events", response_model=List[InventoryEventOut])
async def list_inventory_events(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        logger.warning(
            f"🚫 Unauthorized attempt to access inventory events by {user['username']}"
        )
        raise HTTPException(status_code=403, detail="Admins only")

    try:
        logger.info(f"📦 Admin {user['username']} requested inventory event history")
        query = inventory_events.select().order_by(inventory_events.c.created_at.desc())
        results = await database.fetch_all(query)
        logger.info(
            f"✅ Returned {len(results)} inventory events to {user['username']}"
        )
        return results

    except Exception as e:
        logger.error(f"🔥 Error retrieving inventory events: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected server error")
