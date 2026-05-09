import pytest

from app.core.config import Settings


def make_settings(**overrides: object) -> Settings:
    values = {
        "app_env": "production",
        "app_debug": False,
        "database_url": "postgresql+asyncpg://postgres:postgres@localhost:5432/micro_savings",
        "jwt_secret_key": "production-secret-key-with-at-least-32-chars",
        "backend_cors_origins": ["https://app.example.com"],
        "backend_cors_allow_methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        "backend_cors_allow_headers": ["Accept", "Authorization", "Content-Type"],
        "backend_allowed_hosts": ["api.example.com"],
    }
    values.update(overrides)
    return Settings(**values)


def test_production_safety_validation_accepts_safe_settings() -> None:
    settings = make_settings()

    settings.validate_production_safety()


def test_production_safety_validation_rejects_debug_mode() -> None:
    settings = make_settings(app_debug=True)

    with pytest.raises(RuntimeError, match="APP_DEBUG must be false"):
        settings.validate_production_safety()


def test_production_safety_validation_rejects_example_jwt_secret() -> None:
    settings = make_settings(jwt_secret_key="change-this-before-production-please")

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must not use an example value"):
        settings.validate_production_safety()


def test_production_safety_validation_rejects_missing_cors_origins() -> None:
    settings = make_settings(backend_cors_origins=[])

    with pytest.raises(RuntimeError, match="BACKEND_CORS_ORIGINS must include"):
        settings.validate_production_safety()


def test_production_safety_validation_rejects_localhost_cors_origins() -> None:
    settings = make_settings(backend_cors_origins=["http://localhost:5173"])

    with pytest.raises(RuntimeError, match="must not include localhost"):
        settings.validate_production_safety()


def test_production_safety_validation_rejects_wildcard_allowed_hosts() -> None:
    settings = make_settings(backend_allowed_hosts=["*"])

    with pytest.raises(RuntimeError, match="BACKEND_ALLOWED_HOSTS must list"):
        settings.validate_production_safety()


def test_production_safety_validation_rejects_wildcard_cors_methods() -> None:
    settings = make_settings(backend_cors_allow_methods=["*"])

    with pytest.raises(RuntimeError, match="BACKEND_CORS_ALLOW_METHODS"):
        settings.validate_production_safety()


def test_production_safety_validation_rejects_wildcard_cors_headers() -> None:
    settings = make_settings(backend_cors_allow_headers=["*"])

    with pytest.raises(RuntimeError, match="BACKEND_CORS_ALLOW_HEADERS"):
        settings.validate_production_safety()


def test_production_safety_validation_rejects_empty_allowed_hosts() -> None:
    settings = make_settings(backend_allowed_hosts=[])

    with pytest.raises(RuntimeError, match="BACKEND_ALLOWED_HOSTS must list"):
        settings.validate_production_safety()


def test_non_production_skips_production_safety_validation() -> None:
    settings = make_settings(
        app_env="development",
        app_debug=True,
        jwt_secret_key="change-this-before-production-please",
        backend_cors_origins=["http://localhost:5173"],
        backend_cors_allow_methods=["*"],
        backend_cors_allow_headers=["*"],
        backend_allowed_hosts=["*"],
    )

    settings.validate_production_safety()
