# services/ai_functions.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.models import Product, SaleItem, Sale
from app.db.database import get_db
from fastapi import Depends


def get_top_margin_products(
    store_id: str, days: int = 30, db: Session = Depends(get_db)
):
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        result = (
            db.query(
                Product.name.label("product"),
                func.sum(SaleItem.quantity).label("units_sold"),
                func.sum(SaleItem.price * SaleItem.quantity).label("total_margin"),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(Sale.store_id == store_id)
            .filter(Sale.timestamp >= start_date)
            .group_by(Product.name)
            .order_by(desc("total_margin"))
            .limit(5)
            .all()
        )

        return [
            {
                "product": row.product,
                "units_sold": int(row.units_sold),
                "total_margin": float(row.total_margin),
            }
            for row in result
        ]
    except Exception as e:
        return f"Query failed: {str(e)}"


def get_top_category(store_id: str, days: int = 30, db: Session = Depends(get_db)):
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        result = (
            db.query(
                Product.category,
                func.sum(SaleItem.price * SaleItem.quantity).label("total_margin"),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(Sale.store_id == store_id)
            .filter(Sale.timestamp >= start_date)
            .group_by(Product.category)
            .order_by(desc("total_margin"))
            .limit(1)
            .first()
        )

        if result:
            return f"The top-selling category is {result.category} with ${round(result.total_margin, 2)} in margin."
        else:
            return "No category data available."
    except Exception as e:
        return f"Query failed: {str(e)}"
