from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class SpendingAlert(BaseModel):
    alert_type: Literal[
        "micro_expense",
        "repeated_spending",
        "weekend_spending",
        "behavior_score",
        "budget_breach",
    ]
    severity: Literal["info", "warning", "critical"]
    title: str
    message: str
    nudge: str
    estimated_monthly_impact: Decimal


class SpendingAlertsResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    alerts: list[SpendingAlert]
