# scripts/init_inventory.py

from datetime import datetime
from app.db.database import SessionLocal
from app.models.models import Product, InventoryEvent


def init_inventory_event(product_id: int, change: int, reason: str):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            print(f"❌ Product ID {product_id} not found.")
            return

        # Update inventory quantity
        product.stock_quantity += change
        db.add(product)

        # Insert inventory event
        event = InventoryEvent(
            product_id=product_id,
            change=change,
            reason=reason,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(event)

        db.commit()
        print(
            f"✅ Inventory event created for product ID {product_id} | change={change}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    init_inventory_event(product_id=1, change=10, reason="Initial stock")
