from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal


class SessionSummary(BaseModel):
    cashier_id: int
    cashier_name: str
    opening_cash: Decimal
    closing_cash: Optional[Decimal]
    system_cash_total: Optional[Decimal]
    cash_difference: Optional[Decimal]
    is_over_short: Optional[bool]
    opened_at: datetime
    closed_at: Optional[datetime]


class TopSeller(BaseModel):
    product_id: int
    name: str
    units_sold: int


class ZReportOut(BaseModel):
    date: date
    total_sales: Decimal
    total_cash: Decimal
    total_card: Decimal
    total_returns: Decimal
    sessions: List[SessionSummary]
    top_sellers: List[TopSeller]
