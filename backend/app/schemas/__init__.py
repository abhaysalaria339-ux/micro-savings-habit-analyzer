"""Pydantic schema package."""

from app.schemas.alert import SpendingAlert, SpendingAlertsResponse
from app.schemas.analytics import (
    BehaviorScoreFactor,
    CategorySpendingSummary,
    FinancialBehaviorScore,
    HabitTimelineEvent,
    HabitTimelineResponse,
    MicroExpenseAnalysis,
    MicroExpensePattern,
    MoneyLeakAnalysis,
    MoneyLeakPattern,
    RepeatedSpendingAnalysis,
    RepeatedSpendingPattern,
    SpendingSummary,
    SpendingTrendAnalysis,
    SpendingTrendPoint,
    WeekdayWeekendAnalysis,
    WeekdayWeekendSpendingSegment,
)
from app.schemas.dashboard import DashboardResponse
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.expense import ExpenseCreate, ExpenseListResponse, ExpenseRead, ExpenseUpdate
from app.schemas.goal import GoalCreate, GoalProgressUpdate, GoalRead
from app.schemas.health import HealthCheckResponse, ReadinessCheckResponse
from app.schemas.insight import SavingsInsight, SavingsInsightsResponse
from app.schemas.ml import MLCapability, MLReadinessResponse
from app.schemas.pipeline import (
    DataPipelineResult,
    PipelineCategoryAggregate,
    PipelineFeatureSet,
    ProcessedExpense,
)
from app.schemas.simulator import SavingsSimulationRequest, SavingsSimulationResponse
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, UserLogin, UserRead

__all__ = [
    "CategorySpendingSummary",
    "BehaviorScoreFactor",
    "DataPipelineResult",
    "DashboardResponse",
    "ErrorDetail",
    "ErrorResponse",
    "ExpenseCreate",
    "ExpenseListResponse",
    "ExpenseRead",
    "ExpenseUpdate",
    "FinancialBehaviorScore",
    "GoalCreate",
    "GoalProgressUpdate",
    "GoalRead",
    "HabitTimelineEvent",
    "HabitTimelineResponse",
    "HealthCheckResponse",
    "MoneyLeakAnalysis",
    "MoneyLeakPattern",
    "MLCapability",
    "MLReadinessResponse",
    "PipelineCategoryAggregate",
    "PipelineFeatureSet",
    "ProcessedExpense",
    "MicroExpenseAnalysis",
    "MicroExpensePattern",
    "RepeatedSpendingAnalysis",
    "RepeatedSpendingPattern",
    "ReadinessCheckResponse",
    "SavingsInsight",
    "SavingsInsightsResponse",
    "SavingsSimulationRequest",
    "SavingsSimulationResponse",
    "SpendingAlert",
    "SpendingAlertsResponse",
    "SpendingSummary",
    "SpendingTrendAnalysis",
    "SpendingTrendPoint",
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserRead",
    "WeekdayWeekendAnalysis",
    "WeekdayWeekendSpendingSegment",
]
