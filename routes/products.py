# routes/products.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import Product
from app.models.schemas import ProductCreate, ProductOut
from app.auth.dependencies import get_current_user, require_role
from app.core.logging_config import logger

router = APIRouter()


# 🛒 Product management


# 🔍 Search products by name or SKU (this must go BEFORE `/products/{product_id}`)
@router.get("/products/search", response_model=List[ProductOut])
def search_products(
    query: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query_lower = query.lower()
    products = (
        db.query(Product)
        .filter(
            (Product.name.ilike(f"%{query_lower}%"))
            | (Product.sku.ilike(f"{query_lower}%")),
            Product.tenant_id == current_user["tenant_id"],
        )
        .limit(10)
        .all()
    )
    return products


# 📦 Get full product list
@router.get("/products", response_model=List[ProductOut])
def get_products(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    logger.info("📦 Product list requested")
    try:
        products = (
            db.query(Product)
            .filter(Product.tenant_id == current_user["tenant_id"])
            .order_by(Product.name)
            .all()
        )
        logger.info(f"✅ Returned {len(products)} products")
        return products
    except Exception as e:
        logger.error(f"❌ Failed to fetch products: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching products")


# 🔍 Get product by ID
@router.get("/products/{product_id}", response_model=ProductOut)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"🔍 Fetching product by ID: {product_id}")
    try:
        product = (
            db.query(Product)
            .filter(
                Product.id == product_id, Product.tenant_id == current_user["tenant_id"]
            )
            .first()
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        logger.error(f"❌ Failed to fetch product ID {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching product")


# ➕ Create product
@router.post("/products", response_model=ProductOut)
def create_product(
    new_product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    logger.info(
        f"🛠️ Admin '{current_user['username']}' attempting to create product: {new_product.name}"
    )
    try:
        product = Product(**new_product.dict(), tenant_id=current_user["tenant_id"])
        db.add(product)
        db.commit()
        db.refresh(product)

        logger.info(
            f"✅ Product '{product.name}' created with ID {product.id} by admin '{current_user['username']}'"
        )
        return product
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Product creation failed for '{new_product.name}': {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong")


# 🗑️ Delete product
@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    logger.info(
        f"🗑️ Admin '{current_user['username']}' attempting to delete product ID {product_id}"
    )
    try:
        product = (
            db.query(Product)
            .filter(
                Product.id == product_id, Product.tenant_id == current_user["tenant_id"]
            )
            .first()
        )
        if not product:
            logger.warning(
                f"⚠️ Delete failed: Product ID {product_id} not found by admin '{current_user['username']}'"
            )
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(product)
        db.commit()

        logger.info(
            f"✅ Product ID {product_id} successfully deleted by admin '{current_user['username']}'"
        )
        return {"message": f"Deleted product with ID {product_id}"}
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error deleting product ID {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.get("/categories")
def get_categories(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    categories = (
        db.query(Product.category)
        .filter(Product.tenant_id == current_user["tenant_id"])
        .distinct()
        .order_by(Product.category)
        .all()
    )
    return [c[0] for c in categories if c[0]]
