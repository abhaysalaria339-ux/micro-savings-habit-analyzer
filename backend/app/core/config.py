from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

FORBIDDEN_PRODUCTION_JWT_SECRETS = frozenset(
    {
        "change-this-before-production-please",
    }
)


class Settings(BaseSettings):
    app_name: str = "Micro-Savings Habit Analyzer API"
    app_env: Literal["local", "development", "staging", "production", "test"] = "local"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    max_request_body_bytes: int = Field(default=1_048_576, gt=0)
    rate_limit_requests: int = Field(default=120, gt=0)
    rate_limit_window_seconds: int = Field(default=60, gt=0)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "plain"] = "json"

    database_url: PostgresDsn

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    backend_cors_origins: list[AnyUrl] = Field(default_factory=list)
    backend_cors_allow_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    )
    backend_cors_allow_headers: list[str] = Field(
        default_factory=lambda: ["Accept", "Authorization", "Content-Type"]
    )
    backend_allowed_hosts: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def validate_production_safety(self) -> None:
        if self.app_env != "production":
            return

        errors: list[str] = []

        if self.app_debug:
            errors.append("APP_DEBUG must be false in production")

        if self.jwt_secret_key.strip() in FORBIDDEN_PRODUCTION_JWT_SECRETS:
            errors.append("JWT_SECRET_KEY must not use an example value in production")

        if not self.backend_cors_origins:
            errors.append("BACKEND_CORS_ORIGINS must include the production frontend origin")

        local_origins = [
            str(origin)
            for origin in self.backend_cors_origins
            if str(origin).startswith(("http://localhost", "http://127.0.0.1"))
        ]
        if local_origins:
            errors.append("BACKEND_CORS_ORIGINS must not include localhost origins in production")

        if not self.backend_cors_allow_methods or "*" in self.backend_cors_allow_methods:
            errors.append("BACKEND_CORS_ALLOW_METHODS must not use wildcards in production")

        if not self.backend_cors_allow_headers or "*" in self.backend_cors_allow_headers:
            errors.append("BACKEND_CORS_ALLOW_HEADERS must not use wildcards in production")

        if not self.backend_allowed_hosts or "*" in self.backend_allowed_hosts:
            errors.append("BACKEND_ALLOWED_HOSTS must list production backend hostnames")

        if errors:
            raise RuntimeError("Unsafe production configuration: " + "; ".join(errors))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
