from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get dashboard",
    description="Return combined analytics, insights, alerts, money leaks, and goals.",
)
async def get_dashboard(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> DashboardResponse:
    _validate_date_range(start_date=start_date, end_date=end_date)

    dashboard_service = DashboardService(
        expense_repository=ExpenseRepository(db_session),
        goal_repository=GoalRepository(db_session),
    )
    return await dashboard_service.get_dashboard(
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
