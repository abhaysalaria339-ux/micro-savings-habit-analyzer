from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.insight import SavingsInsightsResponse
from app.services.insight_service import InsightService

router = APIRouter()


@router.get(
    "/savings",
    response_model=SavingsInsightsResponse,
    summary="Get savings insights",
    description="Generate weekly or monthly savings recommendations from spending behavior.",
)
async def get_savings_insights(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    period: Annotated[Literal["weekly", "monthly"], Query()] = "monthly",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SavingsInsightsResponse:
    _validate_date_range(start_date=start_date, end_date=end_date)

    insight_service = InsightService(ExpenseRepository(db_session))
    return await insight_service.get_savings_insights(
        user_id=current_user.id,
        period=period,
        start_date=start_date,
        end_date=end_date,
    )


def _validate_date_range(
    *,
    start_date: datetime | None,
    end_date: datetime | None,
) -> None:
    if (start_date is None) != (end_date is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date and end_date must be provided together.",
        )

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
