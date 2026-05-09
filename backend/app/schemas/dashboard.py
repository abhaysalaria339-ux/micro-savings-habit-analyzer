from datetime import datetime

from pydantic import BaseModel

from app.schemas.alert import SpendingAlert
from app.schemas.analytics import (
    FinancialBehaviorScore,
    MoneyLeakAnalysis,
    SpendingSummary,
    SpendingTrendAnalysis,
)
from app.schemas.goal import GoalRead
from app.schemas.insight import SavingsInsight


class DashboardResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    spending_summary: SpendingSummary
    spending_trends: SpendingTrendAnalysis
    savings_opportunities: list[SavingsInsight]
    behavior_score: FinancialBehaviorScore
    alerts: list[SpendingAlert]
    money_leaks: MoneyLeakAnalysis
    goals: list[GoalRead]
