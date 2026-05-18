from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class RecurringExpenseCandidate(BaseModel):
    category: str
    description: str | None
    occurrence_count: int
    average_amount: Decimal
    total_amount: Decimal
    average_days_between: Decimal | None
    projected_monthly_amount: Decimal
    confidence: Literal["low", "medium", "high"]
    next_expected_at: datetime | None
    recommendation: str


class RecurringExpenseResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    candidates: list[RecurringExpenseCandidate]


class CalendarHeatmapDay(BaseModel):
    day: date
    total_amount: Decimal
    transaction_count: int
    intensity: Literal["none", "low", "medium", "high"]


class CalendarHeatmapResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    max_daily_amount: Decimal
    days: list[CalendarHeatmapDay]


class WeeklyFinancialHealthReport(BaseModel):
    start_date: datetime
    end_date: datetime
    total_spend: Decimal
    previous_total_spend: Decimal
    spend_change_percentage: Decimal
    top_category: str | None
    top_category_amount: Decimal
    recurring_monthly_risk: Decimal
    high_spend_days: int
    summary: str
    recommended_focus: str


class SpendingAnomaly(BaseModel):
    anomaly_type: Literal["large_transaction", "category_spike", "high_spend_day"]
    severity: Literal["info", "warning", "critical"]
    title: str
    description: str
    detected_at: datetime
    amount: Decimal
    category: str | None = None


class HabitCoachRecommendation(BaseModel):
    priority: Literal["low", "medium", "high"]
    title: str
    message: str
    action: str
    estimated_monthly_impact: Decimal


class AdvancedIntelligenceResponse(BaseModel):
    analysis_days: int = Field(ge=7, le=180)
    recurring_expenses: RecurringExpenseResponse
    calendar_heatmap: CalendarHeatmapResponse
    weekly_report: WeeklyFinancialHealthReport
    anomalies: list[SpendingAnomaly]
    coach_recommendations: list[HabitCoachRecommendation]
