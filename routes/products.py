from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.database import database
from app.db.tables import products
from app.schemas import Product, ProductCreate
from app.auth.auth import require_role
from app.logging_config import logger

router = APIRouter()


# 🛒 Product management
@router.get("/products", response_model=List[Product])
async def get_products():
    logger.info("📦 Product list requested")

    try:
        query = products.select()
        result = await database.fetch_all(query)
        logger.info(f"✅ Returned {len(result)} products")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to fetch products: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching products")


@router.post("/products", response_model=Product)
async def create_product(
    new_product: ProductCreate, user: dict = Depends(require_role("admin"))
):
    logger.info(
        f"🛠️ Admin '{user['username']}' attempting to create product: {new_product.name}"
    )

    try:
        query = products.insert().values(
            name=new_product.name,
            sku=new_product.sku,
            price=new_product.price,
            category=new_product.category,
            stock_quantity=new_product.stock_quantity,
        )
        new_id = await database.execute(query)
        logger.info(
            f"✅ Product '{new_product.name}' created with ID {new_id} "
            f"by admin '{user['username']}'"
        )
        return Product(id=new_id, **new_product.dict())

    except Exception as e:
        logger.error(f"❌ Product creation failed for '{new_product.name}': {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, user: dict = Depends(require_role("admin"))):
    logger.info(
        f"🗑️ Admin '{user['username']}' attempting to delete product ID {product_id}"
    )

    try:
        query = products.delete().where(products.c.id == product_id)
        result = await database.execute(query)
        if result:
            logger.info(
                f"✅ Product ID {product_id} successfully deleted by "
                f"admin '{user['username']}'"
            )
            return {"message": f"Deleted product with ID {product_id}"}
        else:
            logger.warning(
                f"⚠️ Delete failed: Product ID {product_id} not found by "
                f"admin '{user['username']}'"
            )
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        logger.error(f"❌ Error deleting product ID {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong")
