from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.ml import MLReadinessResponse
from app.services.ml_readiness_service import MLReadinessService

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
