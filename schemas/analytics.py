# schemas/analytics.py

from pydantic import BaseModel
from typing import Optional


class DailySalesSummary(BaseModel):
    sale_date: str
    day_of_week: str
    total_sales_count: int
    total_sales_value: float
    avg_sale_value: float


class TopProductTrend(BaseModel):
    sale_date: str
    product_id: int
    product_name: str
    units_sold: int
    revenue: float


class InventorySnapshot(BaseModel):
    id: int
    name: str
    category: str
    quantity: int
    price: float


class InventoryMovement(BaseModel):
    product_id: int
    name: str
    category: str
    total_added: int
    total_removed: int
    net_change: int


class TopMarginProduct(BaseModel):
    product_id: int
    name: str
    category: str
    units_sold: int
    revenue: float
    cost_basis: float
    margin_dollars: float
    margin_percent: float


class CategorySales(BaseModel):
    category: str
    total_units_sold: int
    total_revenue: float
    avg_price: float


class KpiSummary(BaseModel):
    total_sales: float
    avg_daily_sales: float
    total_transactions: int
    avg_basket_size: float
    return_rate: float
    top_category: str

    # Add deltas
    delta_total_sales: Optional[float] = None
    delta_avg_daily_sales: Optional[float] = None
    delta_total_transactions: Optional[float] = None
    delta_avg_basket_size: Optional[float] = None
    delta_return_rate: Optional[float] = None

    model_config = {"from_attributes": True}
