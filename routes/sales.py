from fastapi import APIRouter, Depends, HTTPException
from schemas import SaleInput
from tables import products
from app.database import database
from app.auth.auth import get_current_user, require_role
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# 💰 Sales
@router.get("/sales")
async def list_sales():
    logger.info("📄 Retrieving all sales with item details")

    try:
        query = """
            SELECT s.id, s.timestamp, s.total_amount,
                   json_agg(json_build_object(
                       'product_id', si.product_id,
                       'quantity', si.quantity,
                       'price', si.price
                   )) AS items
            FROM sales s
            LEFT JOIN sale_items si ON s.id = si.sale_id
            GROUP BY s.id
            ORDER BY s.timestamp DESC
        """
        results = await database.fetch_all(query=query)
        logger.info(f"✅ {len(results)} sales records retrieved successfully")
        return results

    except Exception as e:
        logger.error(f"❌ Failed to retrieve sales: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sales data")


@router.post("/sales")
async def create_sale(sale: SaleInput, user: dict = Depends(get_current_user)):
    logger.info(
        f"🛒 New sale request by user: {user['username']} "
        f"with {len(sale.items)} item(s)"
    )
    try:
        items = sale.items
        total_amount = 0
        sale_lines = []

        for item in items:
            query = products.select().where(products.c.id == item.product_id)
            product = await database.fetch_one(query)

            if not product:
                logger.warning(f"❌ Product ID {item.product_id} not found")
                raise HTTPException(
                    status_code=404, detail=f"Product {item.product_id} not found"
                )

            if product["stock_quantity"] < item.quantity:
                logger.warning(
                    f"🚫 Insufficient stock for '{product['name']}' "
                    f"(requested: {item.quantity}, "
                    f"available: {product['stock_quantity']})"
                )
                raise HTTPException(
                    status_code=400, detail=f"Insufficient stock for {product['name']}"
                )

            line_total = float(product["price"]) * item.quantity
            total_amount += line_total

            sale_lines.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": float(product["price"]),
                }
            )

        # Insert into sales table
        insert_sale_sql = (
            "INSERT INTO sales (total_amount) VALUES (:total) RETURNING id"
        )
        sale_id = await database.execute(
            query=insert_sale_sql, values={"total": total_amount}
        )
        logger.info(f"💾 Sale {sale_id} recorded with total ${total_amount:.2f}")

        # Insert into sale_items table and update inventory
        for line in sale_lines:
            insert_item_sql = """
                INSERT INTO sale_items (sale_id, product_id, quantity, price)
                VALUES (:sale_id, :product_id, :quantity, :price)
            """
            await database.execute(
                query=insert_item_sql,
                values={
                    "sale_id": sale_id,
                    "product_id": line["product_id"],
                    "quantity": line["quantity"],
                    "price": line["price"],
                },
            )

            await database.execute(
                products.update()
                .where(products.c.id == line["product_id"])
                .values(stock_quantity=products.c.stock_quantity - line["quantity"])
            )
            logger.debug(
                f"🧾 Sale item saved | Product ID {line['product_id']}, "
                f"Qty: {line['quantity']}"
            )
        logger.info(f"✅ Sale {sale_id} completed successfully")
        return {"message": f"Sale {sale_id} completed", "total": total_amount}

    except Exception as e:
        logger.error(f"🔥 Failed to create sale: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected server error")


@router.delete("/sales/{sale_id}")
async def delete_sale(sale_id: int, user: dict = Depends(require_role("admin"))):
    logger.info(f"🗑️ Delete request for sale ID {sale_id} by admin: {user['username']}")

    try:
        # Check if sale exists
        check_sql = "SELECT * FROM sales WHERE id = :id"
        sale = await database.fetch_one(query=check_sql, values={"id": sale_id})
        if not sale:
            logger.warning(f"❌ Sale ID {sale_id} not found for deletion")
            raise HTTPException(status_code=404, detail=f"Sale {sale_id} not found")

        # Delete sale (sale_items will cascade)
        delete_sql = "DELETE FROM sales WHERE id = :id"
        await database.execute(query=delete_sql, values={"id": sale_id})
        logger.info(f"✅ Sale ID {sale_id} deleted successfully by {user['username']}")
        return {"message": f"Sale {sale_id} deleted"}

    except Exception as e:
        logger.error(f"🔥 Failed to delete sale ID {sale_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected server error")
