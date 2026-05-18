from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.request_id import request_id_middleware
from app.middleware.request_logging import request_logging_middleware
from app.middleware.request_size import request_size_limit_middleware
from app.middleware.security_headers import security_headers_middleware


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.backend_allowed_hosts,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).rstrip("/")
            for origin in settings.backend_cors_origins
        ],
        allow_credentials=True,
        allow_methods=settings.backend_cors_allow_methods,
        allow_headers=settings.backend_cors_allow_headers,
    )

    app.middleware("http")(request_id_middleware)
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(security_headers_middleware)
    app.middleware("http")(request_size_limit_middleware)
    app.middleware("http")(rate_limit_middleware)
