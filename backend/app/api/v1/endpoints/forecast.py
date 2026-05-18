from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.settings_repository import SettingsRepository
from app.schemas.forecast import SpendingForecastResponse
from app.services.forecast_service import ForecastService

router = APIRouter()


@router.get("/month-end", response_model=SpendingForecastResponse, summary="Forecast spending")
async def get_month_end_forecast(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> SpendingForecastResponse:
    service = ForecastService(ExpenseRepository(db_session), SettingsRepository(db_session))
    return await service.get_month_end_forecast(user_id=current_user.id)
