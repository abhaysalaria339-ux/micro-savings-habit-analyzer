from fastapi.testclient import TestClient

from app.main import app


def test_default_allowed_hosts_accepts_local_requests() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
