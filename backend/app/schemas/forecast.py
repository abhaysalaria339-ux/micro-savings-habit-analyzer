from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SpendingForecastResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    month_end_projection: Decimal
    current_month_spend: Decimal
    daily_average: Decimal
    projected_savings_gap: Decimal
    confidence: str
    summary: str
