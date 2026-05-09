from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.alert import SpendingAlertsResponse
from app.services.alert_service import AlertService

router = APIRouter()


@router.get(
    "",
    response_model=SpendingAlertsResponse,
    summary="Get spending alerts",
    description="Return context-aware alerts and nudges based on recent spending behavior.",
)
async def get_spending_alerts(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SpendingAlertsResponse:
    _validate_date_range(start_date=start_date, end_date=end_date)

    alert_service = AlertService(ExpenseRepository(db_session))
    return await alert_service.get_spending_alerts(
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
