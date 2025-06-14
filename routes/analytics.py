from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import date, timedelta
import sqlalchemy

from app.db.database import database
from app.db.tables import products
from app.schemas.analytics import (
    DailySalesSummary,
    TopProductTrend,
    InventorySnapshot,
    InventoryMovement,
    TopMarginProduct,
    CategorySales,
)
from app.utils.logger import logger

app = APIRouter()


# Analytics
@app.get("/analytics/sales-summary", response_model=List[DailySalesSummary])
async def sales_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    granularity: str = Query("day", regex="^(day|week|month)$"),
):
    try:
        logger.info(
            f"📈 Sales summary requested: {granularity} from "
            f"{start_date} to {end_date}"
        )

        if granularity == "day":
            date_trunc = "day"
        elif granularity == "week":
            date_trunc = "week"
        else:
            date_trunc = "month"

        sql = f"""
            SELECT
                DATE_TRUNC('{date_trunc}', timestamp) AS sale_date,
                TO_CHAR(DATE_TRUNC('{date_trunc}', timestamp), 'Day') AS day_of_week,
                COUNT(*) AS total_sales_count,
                SUM(total_amount) AS total_sales_value,
                AVG(total_amount) AS avg_sale_value
            FROM sales
            WHERE timestamp BETWEEN :start_date AND :end_date
            GROUP BY sale_date
            ORDER BY sale_date
        """

        rows = await database.fetch_all(
            sql, {"start_date": start_date, "end_date": end_date}
        )
        logger.info(f"✅ Retrieved {len(rows)} records for sales summary")

        # Fill in missing intervals for dashboard consistency
        full_dates = []
        current = start_date
        while current <= end_date:
            full_dates.append(current)
            current += timedelta(
                days=1 if granularity == "day" else 7 if granularity == "week" else 30
            )

        rows_by_date = {row["sale_date"].date(): row for row in rows}
        result = []
        for d in full_dates:
            row = rows_by_date.get(d)
            result.append(
                DailySalesSummary(
                    sale_date=d,
                    day_of_week=row["day_of_week"].strip() if row else d.strftime("%A"),
                    total_sales_count=row["total_sales_count"] if row else 0,
                    total_sales_value=float(row["total_sales_value"]) if row else 0.0,
                    avg_sale_value=float(row["avg_sale_value"]) if row else 0.0,
                )
            )

        return result

    except Exception as e:
        logger.error(f"🔥 Sales summary error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/analytics/top-products")
async def top_products(limit: int = 5, category: Optional[str] = Query(None)):
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

        results = await database.fetch_all(sqlalchemy.text(sql), params)

        logger.info(f"✅ Retrieved {len(results)} top products")
        return results

    except Exception as e:
        logger.error(f"🔥 Top products error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/analytics/top-products-trend", response_model=List[TopProductTrend])
async def top_products_trend(days: int = 30, limit: int = 5):
    try:
        logger.info(f"📈 Product trend requested | Days: {days} | Limit: {limit}")

        # Step 1: Find top product IDs based on total units sold
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
        top_ids_result = await database.fetch_all(
            sqlalchemy.text(top_query), {"days": f"{days} days", "limit": limit}
        )
        top_ids = [r["id"] for r in top_ids_result]

        if not top_ids:
            logger.warning("⚠️ No top products found in time range")
            return []

        # Step 2: Fetch sales trends for top products
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

        trend_result = await database.fetch_all(
            trend_query, {"days": f"{days} days", "product_ids": top_ids}
        )

        logger.info(f"✅ Retrieved trend data for {len(top_ids)} products")
        return [dict(row) for row in trend_result]

    except Exception as e:
        logger.error(f"🔥 Trend analytics error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


# 1. Inventory snapshot
@app.get("/analytics/inventory-snapshot", response_model=List[InventorySnapshot])
async def inventory_snapshot():
    try:
        logger.info("📦 Generating inventory snapshot")

        query = products.select().order_by(products.c.category, products.c.name)
        rows = await database.fetch_all(query)

        logger.info(f"✅ Retrieved {len(rows)} inventory records")
        return rows

    except Exception as e:
        logger.error(f"🔥 Inventory snapshot error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": "Failed to retrieve inventory snapshot"}
        )


# 2. Inventory movement summary (last 30 days)
@app.get("/analytics/inventory-movement", response_model=List[InventoryMovement])
async def inventory_movement():
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
        rows = await database.fetch_all(sql)

        logger.info(f"✅ Retrieved movement data for {len(rows)} products")
        return rows

    except Exception as e:
        logger.error(f"🔥 Inventory movement error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve inventory movement data"},
        )


# 3. Top margin products
@app.get("/analytics/top-margins", response_model=List[TopMarginProduct])
async def top_margins(limit: int = 10):
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
        rows = await database.fetch_all(sql, {"limit": limit})

        logger.info(f"✅ Retrieved top-margin data for {len(rows)} products")
        return rows

    except Exception as e:
        logger.error(f"🔥 Margin report error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": "Failed to fetch top-margin products"}
        )


# 4. Category sales overview
@app.get("/analytics/category-sales", response_model=List[CategorySales])
async def category_sales():
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
        results = await database.fetch_all(sql)

        logger.info(f"✅ Category summary complete for {len(results)} categories")
        return results

    except Exception as e:
        logger.error(f"🔥 Category sales error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": "Failed to fetch category sales"}
        )
