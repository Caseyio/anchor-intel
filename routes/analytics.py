from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import date, timedelta, datetime
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import func, select


from app.db.database import get_db
from app.models.models import SaleItem, Return, Sale, User, Product
from app.models.schemas import ProductReturnRate, SaleReturnRate, CashierReturnRate
from schemas.analytics import (
    DailySalesSummary,
    TopProductTrend,
    InventorySnapshot,
    InventoryMovement,
    TopMarginProduct,
    CategorySales,
    KpiSummary,
)
from app.auth.dependencies import get_current_user
from app.core.logging_config import logger

router = APIRouter()


@router.get("/sales-summary")
def get_sales_summary(
    start_date: str = Query(...),
    end_date: str = Query(...),
    cashier_id: int = Query(None),
    category: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

        logger.info(
            f"📈 Sales summary requested from {start} to {end} (cashier={cashier_id}, category={category})"
        )

        base_query = db.query(
            func.date(Sale.timestamp).label("sale_date"),
            func.count(Sale.id).label("total_sales_count"),
            func.sum(Sale.total_amount).label("total_sales_value"),
            func.avg(Sale.total_amount).label("avg_sale_value"),
        ).filter(
            Sale.timestamp >= start,
            Sale.timestamp < end,
            Sale.tenant_id == current_user.tenant_id,
        )

        if cashier_id:
            base_query = base_query.filter(Sale.cashier_id == cashier_id)

        if category:
            base_query = (
                base_query.join(SaleItem)
                .join(Product)
                .filter(Product.category == category)
            )

        base_query = base_query.group_by(func.date(Sale.timestamp)).order_by(
            func.date(Sale.timestamp)
        )

        results = base_query.all()

        return [
            {
                "sale_date": row.sale_date.isoformat(),
                "total_sales_count": int(row.total_sales_count),
                "total_sales_value": float(row.total_sales_value or 0),
                "avg_sale_value": float(row.avg_sale_value or 0),
                "day_of_week": row.sale_date.strftime("%A"),
            }
            for row in results
        ]

    except Exception as e:
        logger.error(f"🔥 Failed to compute sales summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to compute sales summary")


@router.get("/analytics/top-products")
def top_products(
    limit: int = 5,
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        logger.info(
            f"📊 Top products requested | Limit: {limit} | "
            f"Category: {category or 'All'}"
        )

        sql = """
            SELECT
                p.id,
                p.name,
                p.category,
                SUM(si.quantity) AS total_units_sold,
                SUM(si.quantity * si.price) AS total_revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
        """

        if category:
            sql += " WHERE p.category = :category"

        sql += """
            GROUP BY p.id, p.name, p.category
            ORDER BY total_units_sold DESC
            LIMIT :limit
        """

        params = {"limit": limit}
        if category:
            params["category"] = category

        results = db.execute(sqlalchemy.text(sql), params).fetchall()

        logger.info(f"✅ Retrieved {len(results)} top products")
        return [dict(r._mapping) for r in results]

    except Exception as e:
        logger.error(f"🔥 Top products error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/analytics/top-products-trend", response_model=List[TopProductTrend])
def top_products_trend(days: int = 30, limit: int = 5, db: Session = Depends(get_db)):
    try:
        logger.info(f"📈 Product trend requested | Days: {days} | Limit: {limit}")

        top_query = """
            SELECT p.id
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE s.timestamp >= CURRENT_DATE - INTERVAL :days
            GROUP BY p.id
            ORDER BY SUM(si.quantity) DESC
            LIMIT :limit
        """
        top_ids_result = db.execute(
            sqlalchemy.text(top_query), {"days": f"{days} days", "limit": limit}
        ).fetchall()

        top_ids = [r.id for r in top_ids_result]
        if not top_ids:
            logger.warning("⚠️ No top products found in time range")
            return []

        trend_query = sqlalchemy.text(
            """
            SELECT
                DATE(s.timestamp) AS sale_date,
                p.id AS product_id,
                p.name AS product_name,
                SUM(si.quantity) AS units_sold,
                SUM(si.quantity * si.price) AS revenue
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE s.timestamp >= CURRENT_DATE - INTERVAL :days
              AND p.id = ANY(:product_ids)
            GROUP BY sale_date, p.id, p.name
            ORDER BY sale_date ASC, revenue DESC
            """
        )

        trend_result = db.execute(
            trend_query, {"days": f"{days} days", "product_ids": top_ids}
        ).fetchall()

        logger.info(f"✅ Retrieved trend data for {len(top_ids)} products")
        return [dict(r._mapping) for r in trend_result]

    except Exception as e:
        logger.error(f"🔥 Trend analytics error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/analytics/inventory-snapshot", response_model=List[InventorySnapshot])
def inventory_snapshot(db: Session = Depends(get_db)):
    try:
        logger.info("📦 Generating inventory snapshot")

        products = db.query(Product).order_by(Product.category, Product.name).all()

        logger.info(f"✅ Retrieved {len(products)} inventory records")
        return [
            InventorySnapshot(
                id=p.id,
                name=p.name,
                category=p.category,
                quantity=p.stock_quantity,
                price=float(p.price),
            )
            for p in products
        ]

    except Exception as e:
        logger.error(f"🔥 Inventory snapshot error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": "Failed to retrieve inventory snapshot"}
        )


@router.get("/analytics/inventory-movement", response_model=List[InventoryMovement])
def inventory_movement(db: Session = Depends(get_db)):
    try:
        logger.info("📊 Calculating inventory movement for the past 30 days")

        sql = """
            SELECT
                p.id AS product_id,
                p.name,
                p.category,
                SUM(CASE WHEN ie.change > 0 THEN ie.change ELSE 0 END) AS total_added,
                SUM(
                    CASE WHEN ie.change < 0
                    THEN -ie.change
                    ELSE 0
                END
                ) AS total_removed,
                SUM(ie.change) AS net_change
            FROM inventory_events ie
            JOIN products p ON ie.product_id = p.id
            WHERE ie.timestamp >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY p.id, p.name, p.category
            ORDER BY net_change ASC
        """
        rows = db.execute(sqlalchemy.text(sql)).fetchall()

        logger.info(f"✅ Retrieved movement data for {len(rows)} products")
        return [dict(r._mapping) for r in rows]

    except Exception as e:
        logger.error(f"🔥 Inventory movement error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve inventory movement data"},
        )


@router.get("/analytics/top-margins", response_model=List[TopMarginProduct])
def top_margins(limit: int = 10, db: Session = Depends(get_db)):
    try:
        logger.info(f"📊 Fetching top {limit} products by margin")

        sql = """
            SELECT
                p.id AS product_id,
                p.name,
                p.category,
                SUM(si.quantity) AS units_sold,
                SUM(si.quantity * si.price) AS revenue,
                SUM(si.quantity * COALESCE(p.cost_basis, 0)) AS cost_basis,
                SUM(
                    si.quantity *
                    (si.price - COALESCE(p.cost_basis, 0))
                ) AS margin_dollars,
                CASE
                    WHEN SUM(si.quantity * si.price) > 0 THEN
                        ROUND(
                            100.0 * SUM(si.quantity * (si.price -
                            COALESCE(p.cost_basis, 0))) /
                            SUM(si.quantity * si.price), 2
                        )
                    ELSE 0
                END AS margin_percent
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            GROUP BY p.id, p.name, p.category
            ORDER BY margin_dollars DESC
            LIMIT :limit
        """
        rows = db.execute(sqlalchemy.text(sql), {"limit": limit}).fetchall()

        logger.info(f"✅ Retrieved top-margin data for {len(rows)} products")
        return [dict(r._mapping) for r in rows]

    except Exception as e:
        logger.error(f"🔥 Margin report error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": "Failed to fetch top-margin products"}
        )


@router.get("/analytics/category-sales", response_model=List[CategorySales])
def category_sales(db: Session = Depends(get_db)):
    try:
        logger.info("📊 Generating category-level sales summary")

        sql = """
            SELECT
                category,
                SUM(si.quantity) AS total_units_sold,
                SUM(si.quantity * si.price) AS total_revenue,
                ROUND(
                    SUM(si.quantity * si.price) /
                    NULLIF(SUM(si.quantity), 0),
                    2
                ) AS avg_price
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            GROUP BY category
            ORDER BY total_revenue DESC
        """
        results = db.execute(sqlalchemy.text(sql)).fetchall()

        logger.info(f"✅ Category summary complete for {len(results)} categories")
        return [dict(r._mapping) for r in results]

    except Exception as e:
        logger.error(f"🔥 Category sales error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": "Failed to fetch category sales"}
        )


# --- Return Rate by Product ---
@router.get("/returns/product", response_model=list[ProductReturnRate])
def get_product_return_rates(db: Session = Depends(get_db)):
    sold = (
        db.query(SaleItem.product_id, func.sum(SaleItem.quantity).label("total_sold"))
        .group_by(SaleItem.product_id)
        .subquery()
    )

    returned = (
        db.query(Return.product_id, func.sum(Return.quantity).label("total_returned"))
        .group_by(Return.product_id)
        .subquery()
    )

    joined = (
        db.query(
            Product.id,
            Product.name,
            func.coalesce(sold.c.total_sold, 0),
            func.coalesce(returned.c.total_returned, 0),
        )
        .outerjoin(sold, Product.id == sold.c.product_id)
        .outerjoin(returned, Product.id == returned.c.product_id)
        .all()
    )

    result = []
    for pid, name, sold_qty, returned_qty in joined:
        rate = (returned_qty / sold_qty * 100) if sold_qty else 0.0
        result.append(
            ProductReturnRate(
                product_id=pid,
                product_name=name,
                total_sold=sold_qty,
                total_returned=returned_qty,
                return_rate=round(rate, 2),
            )
        )
    return result


# --- Return Rate by Sale ---
@router.get("/returns/sale", response_model=list[SaleReturnRate])
def get_sale_return_rates(db: Session = Depends(get_db)):
    sale_totals = (
        db.query(
            Sale.id.label("sale_id"),
            func.sum(SaleItem.quantity).label("total_items_sold"),
        )
        .join(SaleItem)
        .group_by(Sale.id)
        .subquery()
    )

    return_totals = (
        db.query(
            Return.sale_id, func.sum(Return.quantity).label("total_items_returned")
        )
        .group_by(Return.sale_id)
        .subquery()
    )

    joined = (
        db.query(
            sale_totals.c.sale_id,
            sale_totals.c.total_items_sold,
            func.coalesce(return_totals.c.total_items_returned, 0),
        )
        .outerjoin(return_totals, sale_totals.c.sale_id == return_totals.c.sale_id)
        .all()
    )

    result = []
    for sid, sold_qty, returned_qty in joined:
        rate = (returned_qty / sold_qty * 100) if sold_qty else 0.0
        result.append(
            SaleReturnRate(
                sale_id=sid,
                total_items_sold=sold_qty,
                total_items_returned=returned_qty,
                return_rate=round(rate, 2),
            )
        )
    return result


# --- Return Rate by Cashier ---
@router.get("/returns/cashier", response_model=list[CashierReturnRate])
def get_cashier_return_rates(db: Session = Depends(get_db)):
    sales_by_user = (
        db.query(Sale.user_id, func.count(Sale.id).label("total_sales"))
        .group_by(Sale.user_id)
        .subquery()
    )

    returns_by_user = (
        db.query(Sale.user_id, func.count(Return.id).label("total_returns"))
        .join(Sale, Sale.id == Return.sale_id)
        .group_by(Sale.user_id)
        .subquery()
    )

    joined = (
        db.query(
            User.id,
            User.username,
            func.coalesce(sales_by_user.c.total_sales, 0),
            func.coalesce(returns_by_user.c.total_returns, 0),
        )
        .outerjoin(sales_by_user, User.id == sales_by_user.c.user_id)
        .outerjoin(returns_by_user, User.id == returns_by_user.c.user_id)
        .all()
    )

    result = []
    for uid, username, sales_count, return_count in joined:
        ratio = return_count / sales_count if sales_count else 0.0
        result.append(
            CashierReturnRate(
                user_id=uid,
                username=username,
                total_returns=return_count,
                total_sales=sales_count,
                return_ratio=round(ratio, 2),
            )
        )
    return result


@router.get("/kpi-summary", response_model=KpiSummary)
def kpi_summary(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD"),
    cashier_id: int = Query(None, description="Optional cashier ID"),
    category: str = Query(None, description="Optional product category"),
    db: Session = Depends(get_db),
):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date() + timedelta(days=1)
        logger.info(
            f"📊 KPI summary requested from {start} to {end} (cashier: {cashier_id}, category: {category})"
        )

        delta_days = (end - start).days
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=delta_days - 1)

        def compute_kpis(start, end):
            sale_query = db.query(Sale).filter(
                Sale.timestamp >= start, Sale.timestamp < end
            )
            if cashier_id:
                sale_query = sale_query.filter(Sale.cashier_id == cashier_id)

            total_sales, total_transactions = sale_query.with_entities(
                func.coalesce(func.sum(Sale.total_amount), 0),
                func.count(Sale.id),
            ).one()

            days_tracked = max((end - start).days, 1)
            avg_daily_sales = total_sales / days_tracked

            # Total units sold
            item_query = (
                db.query(SaleItem)
                .join(Sale)
                .filter(Sale.timestamp >= start, Sale.timestamp < end)
            )
            if cashier_id:
                item_query = item_query.filter(Sale.cashier_id == cashier_id)
            if category:
                item_query = item_query.join(Product).filter(
                    Product.category == category
                )

            total_units = (
                db.query(func.coalesce(func.sum(SaleItem.quantity), 0))
                .select_from(item_query.subquery())
                .scalar()
            )

            avg_basket_size = (
                total_units / total_transactions if total_transactions else 0
            )

            # Return quantity
            return_query = db.query(Return).filter(
                Return.timestamp >= start, Return.timestamp < end
            )
            if category:
                return_query = return_query.join(Product).filter(
                    Product.category == category
                )

            total_returned = (
                db.query(func.coalesce(func.sum(Return.quantity), 0))
                .select_from(return_query.subquery())
                .scalar()
            )

            return_rate = (total_returned / total_units * 100) if total_units else 0

            # Top category (unfiltered for now, or we can filter by cashier if needed)
            top_cat_sql = sqlalchemy.text(
                """
                SELECT p.category, SUM(si.quantity * si.price) AS revenue
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN products p ON si.product_id = p.id
                WHERE s.timestamp >= :start AND s.timestamp < :end
                {cashier_filter}
                {category_filter}
                GROUP BY p.category
                ORDER BY revenue DESC
                LIMIT 1
            """.replace(
                    "{cashier_filter}",
                    "AND s.cashier_id = :cashier_id" if cashier_id else "",
                ).replace(
                    "{category_filter}",
                    "AND p.category = :category" if category else "",
                )
            )

            sql_params = {"start": start, "end": end}
            if cashier_id:
                sql_params["cashier_id"] = cashier_id
            if category:
                sql_params["category"] = category

            top_category_row = db.execute(top_cat_sql, sql_params).fetchone()
            top_category = top_category_row[0] if top_category_row else "N/A"

            return KpiSummary(
                total_sales=round(float(total_sales), 2),
                avg_daily_sales=round(float(avg_daily_sales), 2),
                total_transactions=total_transactions,
                avg_basket_size=round(float(avg_basket_size), 2),
                return_rate=round(float(return_rate), 2),
                top_category=top_category,
            )

        current = compute_kpis(start, end)
        previous = compute_kpis(prev_start, prev_end)

        def safe_delta(curr, prev):
            if prev == 0:
                return 0.0
            return round(((curr - prev) / prev) * 100, 2)

        final_kpi_payload = {
            **current.model_dump(),
            "delta_total_sales": safe_delta(current.total_sales, previous.total_sales),
            "delta_avg_daily_sales": safe_delta(
                current.avg_daily_sales, previous.avg_daily_sales
            ),
            "delta_total_transactions": safe_delta(
                current.total_transactions, previous.total_transactions
            ),
            "delta_avg_basket_size": safe_delta(
                current.avg_basket_size, previous.avg_basket_size
            ),
            "delta_return_rate": safe_delta(current.return_rate, previous.return_rate),
        }

        logger.info("📦 Final KPI summary payload: %s", final_kpi_payload)

        return final_kpi_payload

    except Exception as e:
        logger.error(f"🔥 KPI summary error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to compute KPI summary")
