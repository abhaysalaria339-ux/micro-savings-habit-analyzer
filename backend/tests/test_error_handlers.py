from fastapi.testclient import TestClient

from app.main import app


def test_validation_error_response_shape() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "short",
        },
    )

    body = response.json()

    assert response.status_code == 422
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Request validation failed."
    assert isinstance(body["error"]["details"], list)
