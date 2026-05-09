from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class SavingsInsight(BaseModel):
    insight_type: Literal["micro_expense", "repeated_spending", "category_concentration"]
    title: str
    message: str
    action: str
    estimated_monthly_savings: Decimal


class SavingsInsightsResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    period: Literal["weekly", "monthly"]
    total_estimated_monthly_savings: Decimal
    insights: list[SavingsInsight]
