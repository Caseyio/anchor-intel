from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel


# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # 'admin' or 'cashier'


class UserOut(BaseModel):
    id: int
    username: str
    role: str


class LoginInput(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Inventory models
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


# Product
class Product(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    category: str
    stock_quantity: int


class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float
    category: str
    stock_quantity: int


# Sales
class SaleItemInput(BaseModel):
    product_id: int
    quantity: int


class SaleInput(BaseModel):
    items: List[SaleItemInput]


class DailySalesSummary(BaseModel):
    sale_date: date
    day_of_week: str
    total_sales_count: int
    total_sales_value: float
    avg_sale_value: float


# Analytics Models
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
