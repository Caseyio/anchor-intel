# routes/returns.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.models.models import Product, Return as ReturnRecord, Sale, SaleItem, User
from app.models.schemas import ReturnCreateBatch, ReturnRecord as ReturnOut

router = APIRouter(prefix="/returns", tags=["Returns"])


@router.post("/", response_model=List[ReturnOut])
def submit_return(
    batch: ReturnCreateBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_returns = []

    if batch.sale_id:
        sale = (
            db.query(Sale)
            .filter(Sale.id == batch.sale_id, Sale.tenant_id == current_user.tenant_id)
            .first()
        )
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found.")

        original_items = {item.product_id: item.quantity for item in sale.items}
        prior_returns = (
            db.query(ReturnRecord).filter(ReturnRecord.sale_id == batch.sale_id).all()
        )

        returned_qty = {}
        for r in prior_returns:
            returned_qty[r.product_id] = returned_qty.get(r.product_id, 0) + r.quantity

        has_valid_item = False
        for ret in batch.returns:
            if not ret.reason:
                raise HTTPException(
                    status_code=400, detail="Each return must include a reason."
                )

            if ret.product_id not in original_items:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product ID {ret.product_id} not in original sale.",
                )

            allowable = original_items[ret.product_id] - returned_qty.get(
                ret.product_id, 0
            )
            if allowable <= 0:
                continue

            if ret.quantity > allowable:
                raise HTTPException(
                    status_code=400,
                    detail=f"Too many returned for product ID {ret.product_id}. Max allowed: {allowable}",
                )

            has_valid_item = True

        if not has_valid_item:
            raise HTTPException(
                status_code=400,
                detail="All items in this sale have already been returned.",
            )

    for ret in batch.returns:
        if not ret.reason:
            raise HTTPException(
                status_code=400, detail="Each return must include a reason."
            )

        product = (
            db.query(Product)
            .filter(
                Product.id == ret.product_id,
                Product.tenant_id == current_user.tenant_id,
            )
            .first()
        )
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product ID {ret.product_id} not found."
            )

        if ret.restock:
            product.stock_quantity += ret.quantity

        return_record = ReturnRecord(
            product_id=ret.product_id,
            quantity=ret.quantity,
            reason=ret.reason,
            notes=ret.notes,
            sale_id=batch.sale_id if batch.sale_id else None,
            tenant_id=current_user.tenant_id,
        )
        db.add(return_record)
        saved_returns.append(return_record)

    db.commit()
    return saved_returns
