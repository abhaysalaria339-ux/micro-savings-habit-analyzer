from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health import HealthCheckResponse, ReadinessCheckResponse


class HealthService:
    @staticmethod
    def get_liveness() -> HealthCheckResponse:
        return HealthCheckResponse(status="ok")

    @staticmethod
    async def get_readiness(db_session: AsyncSession) -> ReadinessCheckResponse:
        await db_session.execute(text("SELECT 1"))
        return ReadinessCheckResponse(status="ok", database="reachable")
