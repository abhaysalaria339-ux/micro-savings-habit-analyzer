from fastapi.testclient import TestClient

from app.main import app


def test_openapi_documents_common_error_response_schema() -> None:
    client = TestClient(app)

    schema = client.get("/openapi.json").json()

    expense_list_responses = schema["paths"]["/api/v1/expenses"]["get"]["responses"]
    assert "401" in expense_list_responses
    assert "422" in expense_list_responses
    assert "500" in expense_list_responses
    assert (
        expense_list_responses["401"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/ErrorResponse"
    )
    assert "ErrorResponse" in schema["components"]["schemas"]


def test_openapi_documents_jwt_bearer_authentication() -> None:
    client = TestClient(app)

    schema = client.get("/openapi.json").json()

    security_schemes = schema["components"]["securitySchemes"]
    assert "OAuth2PasswordBearer" in security_schemes
    assert security_schemes["OAuth2PasswordBearer"]["type"] == "oauth2"
    assert (
        security_schemes["OAuth2PasswordBearer"]["flows"]["password"]["tokenUrl"]
        == "/api/v1/auth/login"
    )
