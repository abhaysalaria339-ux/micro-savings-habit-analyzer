from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.advanced import AdvancedIntelligenceResponse
from app.services.advanced_intelligence_service import AdvancedIntelligenceService

router = APIRouter()


@router.get(
    "/intelligence",
    response_model=AdvancedIntelligenceResponse,
    summary="Get advanced spending intelligence",
    description=(
        "Return recurring expense candidates, calendar heatmap data, weekly health report, "
        "anomaly signals, and habit coach recommendations."
    ),
)
async def get_advanced_intelligence(
    analysis_days: Annotated[int, Query(ge=7, le=180)] = 90,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> AdvancedIntelligenceResponse:
    service = AdvancedIntelligenceService(ExpenseRepository(db_session))
    return await service.get_advanced_intelligence(
        user_id=current_user.id,
        analysis_days=analysis_days,
    )
