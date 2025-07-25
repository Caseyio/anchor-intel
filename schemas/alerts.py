# schemas/alerts.py
from pydantic import BaseModel


class LowStockAlert(BaseModel):
    product_id: int
    name: str
    stock_level: int
