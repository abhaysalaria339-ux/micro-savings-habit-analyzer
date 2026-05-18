"""Pydantic schema package."""

from app.schemas.advanced import (
    AdvancedIntelligenceResponse,
    CalendarHeatmapDay,
    CalendarHeatmapResponse,
    HabitCoachRecommendation,
    RecurringExpenseCandidate,
    RecurringExpenseResponse,
    SpendingAnomaly,
    WeeklyFinancialHealthReport,
)
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
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.schemas.dashboard import DashboardResponse
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseDuplicateCheckResponse,
    ExpenseImportRequest,
    ExpenseImportResponse,
    ExpenseImportRowResult,
    ExpenseListResponse,
    ExpenseRead,
    ExpenseUpdate,
)
from app.schemas.goal import (
    GoalCreate,
    GoalProgressUpdate,
    GoalRead,
    GoalSuggestion,
    GoalSuggestionsResponse,
)
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
    "AdvancedIntelligenceResponse",
    "BehaviorScoreFactor",
    "BudgetCreate",
    "BudgetRead",
    "BudgetUpdate",
    "CalendarHeatmapDay",
    "CalendarHeatmapResponse",
    "CategorySpendingSummary",
    "DataPipelineResult",
    "DashboardResponse",
    "ErrorDetail",
    "ErrorResponse",
    "ExpenseCreate",
    "ExpenseDuplicateCheckResponse",
    "ExpenseImportRequest",
    "ExpenseImportResponse",
    "ExpenseImportRowResult",
    "ExpenseListResponse",
    "ExpenseRead",
    "ExpenseUpdate",
    "FinancialBehaviorScore",
    "GoalCreate",
    "GoalProgressUpdate",
    "GoalRead",
    "GoalSuggestion",
    "GoalSuggestionsResponse",
    "HabitCoachRecommendation",
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
    "RecurringExpenseCandidate",
    "RecurringExpenseResponse",
    "RepeatedSpendingAnalysis",
    "RepeatedSpendingPattern",
    "ReadinessCheckResponse",
    "SavingsInsight",
    "SavingsInsightsResponse",
    "SavingsSimulationRequest",
    "SavingsSimulationResponse",
    "SpendingAlert",
    "SpendingAlertsResponse",
    "SpendingAnomaly",
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
    "WeeklyFinancialHealthReport",
]
