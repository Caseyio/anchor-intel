from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID

# --------------------
# 🔐 User Auth Schemas
# --------------------


class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # 'admin' or 'cashier'
    tenant_id: Optional[UUID] = None


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    tenant_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class LoginInput(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------------------------
# 📦 Product & Inventory
# -------------------------


class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float
    category: str
    stock_quantity: int
    tenant_id: Optional[UUID] = None


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    category: str
    stock_quantity: int
    tenant_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class InventoryEventIn(BaseModel):
    product_id: int
    change: int
    reason: Optional[str] = None


class InventoryEventOut(BaseModel):
    id: int
    product_id: int
    change: int
    reason: Optional[str]
    created_at: datetime
    tenant_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


# --------------------
# 💰 Sales & Items
# --------------------


class SaleItemInput(BaseModel):
    product_id: int
    quantity: int


class SaleItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class SaleCreate(BaseModel):
    total_amount: float
    timestamp: Optional[datetime] = None
    payment_type: str
    items: List[SaleItem]
    tenant_id: Optional[UUID] = None


class SaleInput(BaseModel):
    items: List[SaleItemInput]


class SaleItemOut(BaseModel):
    id: int
    product_id: int
    name: Optional[str] = None
    sku: Optional[str] = None
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class SaleOut(BaseModel):
    id: int
    total_amount: float
    timestamp: datetime
    updated_at: Optional[datetime]
    payment_type: str
    items: List[SaleItemOut]
    tenant_id: Optional[UUID] = None

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }


# --------------------
# 🔁 Returns
# --------------------


class ReturnItem(BaseModel):
    product_id: int
    quantity: int
    restock: bool = True
    reason: str
    notes: Optional[str] = None


class ReturnCreate(BaseModel):
    product_id: int
    quantity: int
    reason: str
    notes: Optional[str] = None
    restock: bool = True


class ReturnCreateBatch(BaseModel):
    sale_id: Optional[int] = None  # null = manual return
    returns: List[ReturnCreate]


class ReturnRecord(BaseModel):
    id: int
    product_id: int
    quantity: int
    reason: str
    notes: Optional[str]
    created_at: Optional[datetime] = None
    tenant_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


# --------------------
# 📊 Analytics
# --------------------


class KpiSummary(BaseModel):
    total_sales: float
    avg_daily_sales: float
    total_transactions: int
    avg_basket_size: float
    return_rate: float
    top_category: str

    delta_total_sales: Optional[float] = None
    delta_avg_daily_sales: Optional[float] = None
    delta_total_transactions: Optional[float] = None
    delta_avg_basket_size: Optional[float] = None
    delta_return_rate: Optional[float] = None

    model_config = {"from_attributes": True}


class DailySalesSummary(BaseModel):
    sale_date: str
    day_of_week: str
    total_sales_count: int
    total_sales_value: float
    avg_sale_value: float


class TopProductTrend(BaseModel):
    period: date
    product_id: int
    product_name: str
    total_units_sold: int
    total_revenue: float


class InventorySnapshot(BaseModel):
    product_id: int
    name: str
    sku: str
    category: str
    stock_quantity: int


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


class LowStockAlert(BaseModel):
    product_id: int
    name: str
    category: str
    stock_quantity: int


class ProductReturnRate(BaseModel):
    product_id: int
    product_name: str
    total_sold: int
    total_returned: int
    return_rate: float


class SaleReturnRate(BaseModel):
    sale_id: int
    total_items_sold: int
    total_items_returned: int
    return_rate: float


class CashierReturnRate(BaseModel):
    user_id: int
    username: str
    total_returns: int
    total_sales: int
    return_ratio: float


# --------------------
# 💼 Cashier Sessions
# --------------------


class CashierSessionCreate(BaseModel):
    opening_cash: Decimal
    terminal_id: Optional[str] = None
    notes: Optional[str] = None


class CashierSessionClose(BaseModel):
    closing_cash: Decimal
    notes: Optional[str] = None


class CashierSessionOut(BaseModel):
    id: int
    cashier_id: int
    terminal_id: Optional[str]
    opened_at: datetime
    closed_at: Optional[datetime]
    opening_cash: Decimal
    closing_cash: Optional[Decimal]
    system_cash_total: Optional[Decimal]
    cash_difference: Optional[Decimal]
    is_over_short: Optional[bool]
    notes: Optional[str]
    tenant_id: Optional[UUID] = None

    model_config = {"from_attributes": True}
