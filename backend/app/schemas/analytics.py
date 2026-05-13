from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class CategorySpendingSummary(BaseModel):
    category: str
    total_amount: Decimal
    transaction_count: int
    percentage_of_total: Decimal


class SpendingSummary(BaseModel):
    start_date: datetime | None
    end_date: datetime | None
    total_amount: Decimal
    transaction_count: int
    average_expense_amount: Decimal
    categories: list[CategorySpendingSummary]


class MicroExpensePattern(BaseModel):
    category: str
    description: str | None
    occurrence_count: int
    average_amount: Decimal
    total_amount: Decimal
    projected_monthly_amount: Decimal
    latest_spent_at: datetime


class MicroExpenseAnalysis(BaseModel):
    start_date: datetime
    end_date: datetime
    max_expense_amount: Decimal
    min_occurrences: int
    total_micro_expense_amount: Decimal
    patterns: list[MicroExpensePattern]


class WeekdayWeekendSpendingSegment(BaseModel):
    period_type: str
    total_amount: Decimal
    transaction_count: int
    average_expense_amount: Decimal
    percentage_of_total: Decimal


class WeekdayWeekendAnalysis(BaseModel):
    start_date: datetime
    end_date: datetime
    total_amount: Decimal
    weekday: WeekdayWeekendSpendingSegment
    weekend: WeekdayWeekendSpendingSegment
    higher_spending_period: str | None
    difference_amount: Decimal


class RepeatedSpendingPattern(BaseModel):
    category: str
    description: str | None
    occurrence_count: int
    total_amount: Decimal
    average_amount: Decimal
    first_spent_at: datetime
    latest_spent_at: datetime
    average_days_between: Decimal | None


class RepeatedSpendingAnalysis(BaseModel):
    start_date: datetime
    end_date: datetime
    min_occurrences: int
    total_repeated_amount: Decimal
    patterns: list[RepeatedSpendingPattern]


class BehaviorScoreFactor(BaseModel):
    name: str
    impact: int
    message: str


class FinancialBehaviorScore(BaseModel):
    start_date: datetime
    end_date: datetime
    score: int
    classification: Literal["Saver", "Neutral", "Spender"]
    total_amount: Decimal
    transaction_count: int
    factors: list[BehaviorScoreFactor]


class MoneyLeakPattern(BaseModel):
    category: str
    description: str | None
    occurrence_count: int
    total_amount: Decimal
    average_amount: Decimal
    projected_monthly_leak: Decimal
    average_days_between: Decimal | None
    leak_risk: Literal["low", "medium", "high"]
    reason: str


class MoneyLeakAnalysis(BaseModel):
    start_date: datetime
    end_date: datetime
    total_leak_amount: Decimal
    projected_monthly_leak: Decimal
    patterns: list[MoneyLeakPattern]


class MoneyLeakScoreEvidence(BaseModel):
    name: str
    impact: int
    message: str


class MoneyLeakScore(BaseModel):
    start_date: datetime
    end_date: datetime
    score: int
    risk_level: Literal["low", "medium", "high", "critical"]
    projected_monthly_leak: Decimal
    leak_ratio: Decimal
    pattern_count: int
    top_leak_category: str | None
    summary: str
    recommended_action: str
    evidence: list[MoneyLeakScoreEvidence]


class HabitTimelineEvent(BaseModel):
    event_type: Literal[
        "micro_spending",
        "weekend_shift",
        "category_focus",
        "money_leak",
        "positive_signal",
        "spending_trend",
    ]
    severity: Literal["info", "positive", "warning", "critical"]
    title: str
    description: str
    happened_at: datetime
    amount: Decimal | None = None
    category: str | None = None
    action: str


class HabitTimelineResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    events: list[HabitTimelineEvent]


class SpendingTrendPoint(BaseModel):
    period_start: datetime
    total_amount: Decimal
    transaction_count: int
    average_expense_amount: Decimal


class SpendingTrendAnalysis(BaseModel):
    start_date: datetime
    end_date: datetime
    interval: Literal["daily", "weekly", "monthly"]
    total_amount: Decimal
    points: list[SpendingTrendPoint]
