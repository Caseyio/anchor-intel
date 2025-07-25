# routes/sales.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.models import Product, Sale, SaleItem
from app.models.schemas import SaleInput, SaleCreate, SaleOut
from app.auth.dependencies import get_current_user, require_role
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/sales")
def list_sales(db: Session = Depends(get_db)):
    logger.info("📄 Retrieving all sales with item details")
    try:
        sales = db.query(Sale).order_by(Sale.timestamp.desc()).all()
        results = [
            {
                "id": s.id,
                "timestamp": s.timestamp,
                "total_amount": float(s.total_amount),
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": float(item.price),
                    }
                    for item in s.items
                ],
            }
            for s in sales
        ]
        logger.info(f"✅ {len(results)} sales records retrieved successfully")
        return results
    except Exception as e:
        logger.error(f"❌ Failed to retrieve sales: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sales data")


@router.get("/sales/by-product", response_model=List[SaleOut])
def get_sales_by_product(query: str, db: Session = Depends(get_db)):
    product_ids = (
        db.query(Product.id)
        .filter((Product.name.ilike(f"%{query}%")) | (Product.sku.ilike(f"%{query}%")))
        .subquery()
    )

    sale_ids = (
        db.query(SaleItem.sale_id)
        .filter(SaleItem.product_id.in_(db.query(product_ids)))
        .distinct()
        .subquery()
    )

    sales = (
        db.query(Sale)
        .filter(Sale.id.in_(db.query(sale_ids)))
        .order_by(Sale.timestamp.desc())
        .all()
    )

    return sales


@router.get("/sales/{sale_id}", response_model=SaleOut)
def get_sale_by_id(sale_id: int, db: Session = Depends(get_db)):
    sale = (
        db.query(Sale)
        .options(joinedload(Sale.items).joinedload(SaleItem.product))
        .filter(Sale.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    for item in sale.items:
        item.name = item.product.name if item.product else None
        item.sku = item.product.sku if item.product else None

    return sale


@router.post("/sales/checkout")
def checkout(sale: SaleCreate, db: Session = Depends(get_db)):
    try:
        logger.info("🧾 Incoming sale payload: %s", sale.dict())

        new_sale = Sale(
            total_amount=sale.total_amount,
            timestamp=sale.timestamp or datetime.utcnow(),
            updated_at=datetime.utcnow(),
            payment_type=sale.payment_type,
        )
        db.add(new_sale)
        db.flush()

        for item in sale.items:
            db.add(
                SaleItem(
                    sale_id=new_sale.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                )
            )
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity -= item.quantity

        db.commit()
        return {"message": "Sale completed", "sale_id": new_sale.id}
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Checkout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")


@router.post("/sales")
def create_sale(
    sale: SaleInput,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(
        f"🛒 New sale request by user: {user['username']} with {len(sale.items)} item(s)"
    )
    try:
        total_amount = 0
        sale_items = []

        for item in sale.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product {item.product_id} not found"
                )
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400, detail=f"Insufficient stock for {product.name}"
                )

            total_amount += float(product.price) * item.quantity

            sale_items.append(
                SaleItem(
                    product_id=product.id, quantity=item.quantity, price=product.price
                )
            )

            product.stock_quantity -= item.quantity

        new_sale = Sale(
            total_amount=total_amount,
            cashier_id=user["id"],
            payment_type=sale.payment_type,
        )
        db.add(new_sale)
        db.flush()

        for item in sale_items:
            item.sale_id = new_sale.id
            db.add(item)

        db.commit()
        logger.info(f"✅ Sale {new_sale.id} completed successfully")
        return {"message": f"Sale {new_sale.id} completed", "total": total_amount}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"🔥 Failed to create sale: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected server error")


@router.delete("/sales/{sale_id}")
def delete_sale(
    sale_id: int,
    user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    logger.info(f"🗑️ Delete request for sale ID {sale_id} by admin: {user['username']}")
    try:
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(status_code=404, detail=f"Sale {sale_id} not found")

        db.delete(sale)
        db.commit()

        logger.info(f"✅ Sale ID {sale_id} deleted successfully by {user['username']}")
        return {"message": f"Sale {sale_id} deleted"}

    except Exception as e:
        db.rollback()
        logger.error(f"🔥 Failed to delete sale ID {sale_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected server error")
