import logging

from fastapi.testclient import TestClient

from app.main import app
from app.middleware.request_id import REQUEST_ID_HEADER


def test_request_logging_includes_request_context(caplog) -> None:
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="app.request"):
        response = client.get(
            "/api/v1/health",
            headers={REQUEST_ID_HEADER: "test-request-id"},
        )

    assert response.status_code == 200

    request_log = next(
        record for record in caplog.records if record.name == "app.request"
    )
    assert request_log.request_id == "test-request-id"
    assert request_log.event == "request_completed"
    assert request_log.method == "GET"
    assert request_log.path == "/api/v1/health"
    assert request_log.route == "/api/v1/health"
    assert request_log.status_code == 200


def test_request_logging_omits_query_string(caplog) -> None:
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="app.request"):
        response = client.get("/api/v1/health?token=secret-value")

    assert response.status_code == 200

    request_log = next(
        record for record in caplog.records if record.name == "app.request"
    )
    assert request_log.path == "/api/v1/health"
    assert "secret-value" not in request_log.getMessage()


def test_request_logging_uses_warning_for_client_errors(caplog) -> None:
    client = TestClient(app)

    with caplog.at_level(logging.WARNING, logger="app.request"):
        response = client.get("/api/v1/missing")

    assert response.status_code == 404

    request_log = next(
        record for record in caplog.records if record.name == "app.request"
    )
    assert request_log.levelno == logging.WARNING
    assert request_log.status_code == 404
