from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.ml import MLReadinessResponse, MLSpendingProfileResponse
from app.services.ml_readiness_service import MLReadinessService
from app.services.ml_spending_profile_service import MLSpendingProfileService

router = APIRouter()


@router.get(
    "/readiness",
    response_model=MLReadinessResponse,
    summary="Get ML readiness",
    description="Return architecture readiness information for future ML capabilities.",
)
async def get_ml_readiness(
    current_user: User = Depends(get_current_active_user),
) -> MLReadinessResponse:
    _ = current_user
    return MLReadinessService().get_readiness()


@router.get(
    "/spending-profile",
    response_model=MLSpendingProfileResponse,
    summary="Get ML spending profile",
    description=(
        "Return an explainable spending profile cluster from recent expense behavior. "
        "This is a lightweight ML prototype and does not train a model on request."
    ),
)
async def get_ml_spending_profile(
    analysis_days: Annotated[int, Query(ge=14, le=365)] = 90,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> MLSpendingProfileResponse:
    service = MLSpendingProfileService(ExpenseRepository(db_session))
    return await service.get_spending_profile(
        user_id=current_user.id,
        analysis_days=analysis_days,
    )
