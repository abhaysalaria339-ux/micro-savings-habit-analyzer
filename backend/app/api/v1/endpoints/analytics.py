from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.analytics import (
    FinancialBehaviorScore,
    HabitTimelineResponse,
    MicroExpenseAnalysis,
    MoneyLeakAnalysis,
    MoneyLeakScore,
    RepeatedSpendingAnalysis,
    SpendingSummary,
    SpendingTrendAnalysis,
    WeekdayWeekendAnalysis,
)
from app.schemas.pipeline import DataPipelineResult
from app.services.analytics_service import AnalyticsService
from app.services.data_pipeline_service import DataPipelineService

router = APIRouter()


@router.get(
    "/spending-summary",
    response_model=SpendingSummary,
    summary="Get spending summary",
    description="Return total, average, count, and category-level spending for a date range.",
)
async def get_spending_summary(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SpendingSummary:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.get_spending_summary(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/micro-expenses",
    response_model=MicroExpenseAnalysis,
    summary="Detect micro-expenses",
    description="Find small repeated expenses and estimate their cumulative impact.",
)
async def detect_micro_expenses(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    max_expense_amount: Annotated[Decimal, Query(gt=0)] = Decimal("100.00"),
    min_occurrences: Annotated[int, Query(ge=2, le=100)] = 3,
) -> MicroExpenseAnalysis:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.detect_micro_expenses(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        max_expense_amount=max_expense_amount,
        min_occurrences=min_occurrences,
    )


@router.get(
    "/weekday-weekend",
    response_model=WeekdayWeekendAnalysis,
    summary="Compare weekday and weekend spending",
    description="Compare spending behavior between weekdays and weekends.",
)
async def compare_weekday_weekend_spending(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> WeekdayWeekendAnalysis:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.compare_weekday_weekend_spending(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/repeated-spending",
    response_model=RepeatedSpendingAnalysis,
    summary="Detect repeated spending",
    description="Find recurring category and description patterns across a date range.",
)
async def detect_repeated_spending(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    min_occurrences: Annotated[int, Query(ge=2, le=100)] = 3,
) -> RepeatedSpendingAnalysis:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.detect_repeated_spending(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        min_occurrences=min_occurrences,
    )


@router.get(
    "/behavior-score",
    response_model=FinancialBehaviorScore,
    summary="Calculate behavior score",
    description="Classify the user's financial behavior as saver, neutral, or spender.",
)
async def get_financial_behavior_score(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> FinancialBehaviorScore:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.calculate_financial_behavior_score(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/money-leaks",
    response_model=MoneyLeakAnalysis,
    summary="Detect money leaks",
    description="Find unnoticed recurring spending patterns that may become savings opportunities.",
)
async def detect_money_leaks(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    min_occurrences: Annotated[int, Query(ge=2, le=100)] = 3,
) -> MoneyLeakAnalysis:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.detect_money_leaks(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        min_occurrences=min_occurrences,
    )


@router.get(
    "/money-leak-score",
    response_model=MoneyLeakScore,
    summary="Calculate money leak score",
    description="Return an explainable risk score for invisible recurring money leaks.",
)
async def calculate_money_leak_score(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> MoneyLeakScore:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.calculate_money_leak_score(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/spending-trends",
    response_model=SpendingTrendAnalysis,
    summary="Analyze spending trends",
    description="Return daily, weekly, or monthly spending trend points.",
)
async def analyze_spending_trends(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    interval: Annotated[Literal["daily", "weekly", "monthly"], Query()] = "daily",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SpendingTrendAnalysis:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.analyze_spending_trends(
        user_id=current_user.id,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/habit-timeline",
    response_model=HabitTimelineResponse,
    summary="Build habit timeline",
    description="Return behavior-focused timeline events from spending patterns.",
)
async def build_habit_timeline(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 8,
) -> HabitTimelineResponse:
    _validate_date_range(start_date=start_date, end_date=end_date)

    analytics_service = AnalyticsService(ExpenseRepository(db_session))
    return await analytics_service.build_habit_timeline(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@router.get(
    "/data-pipeline",
    response_model=DataPipelineResult,
    summary="Run data pipeline",
    description="Run cleaning, aggregation, feature engineering, and insight generation.",
)
async def run_data_pipeline(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> DataPipelineResult:
    _validate_date_range(start_date=start_date, end_date=end_date)

    data_pipeline_service = DataPipelineService(ExpenseRepository(db_session))
    return await data_pipeline_service.run_expense_pipeline(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


def _validate_date_range(
    *,
    start_date: datetime | None,
    end_date: datetime | None,
) -> None:
    if start_date is None or end_date is None:
        return

    try:
        is_invalid_range = start_date > end_date
    except TypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date and end_date must both include timezone offsets or both omit them.",
        ) from exc

    if is_invalid_range:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date.",
        )
