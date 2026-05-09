from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.middleware.request_id import REQUEST_ID_HEADER
from app.services.health_service import HealthService


def test_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert REQUEST_ID_HEADER in response.headers


async def test_health_service_checks_database_readiness() -> None:
    db_session = AsyncMock()

    response = await HealthService.get_readiness(db_session)

    db_session.execute.assert_awaited_once()
    assert response.model_dump() == {"status": "ok", "database": "reachable"}
