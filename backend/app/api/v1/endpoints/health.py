from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.health import HealthCheckResponse, ReadinessCheckResponse
from app.services.health_service import HealthService

router = APIRouter()


@router.get(
    "",
    response_model=HealthCheckResponse,
    summary="Check API liveness",
    description="Return a lightweight liveness response for the API process.",
)
async def health_check() -> HealthCheckResponse:
    return HealthService.get_liveness()


@router.get(
    "/db",
    response_model=ReadinessCheckResponse,
    summary="Check database readiness",
    description="Verify the API can execute a simple database query.",
)
async def database_health_check(
    db_session: AsyncSession = Depends(get_db_session),
) -> ReadinessCheckResponse:
    return await HealthService.get_readiness(db_session)
