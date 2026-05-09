from fastapi.testclient import TestClient

from app.main import app


def test_oversized_request_body_is_rejected() -> None:
    client = TestClient(app)
    oversized_body = b"x" * (1_048_576 + 1)

    response = client.post(
        "/api/v1/auth/register",
        content=oversized_body,
        headers={"Content-Type": "application/json"},
    )

    body = response.json()

    assert response.status_code == 413
    assert body["error"]["code"] == "request_too_large"
    assert body["error"]["message"] == "Request body is too large."
    assert body["error"]["details"]["max_request_body_bytes"] == 1_048_576
