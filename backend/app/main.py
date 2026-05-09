from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.setup import register_middleware

OPENAPI_TAGS = [
    {
        "name": "auth",
        "description": "User registration, login, and current-user profile access.",
    },
    {
        "name": "expenses",
        "description": "Expense capture and expense record management.",
    },
    {
        "name": "analytics",
        "description": "Behavioral spending analysis and money leak detection.",
    },
    {
        "name": "insights",
        "description": "Actionable savings recommendations.",
    },
    {
        "name": "alerts",
        "description": "Context-aware spending nudges and warnings.",
    },
    {
        "name": "goals",
        "description": "Savings goals and progress tracking.",
    },
    {
        "name": "simulator",
        "description": "What-if savings projection tools.",
    },
    {
        "name": "dashboard",
        "description": "Aggregated dashboard data for the frontend.",
    },
    {
        "name": "ml",
        "description": "Future-ready machine learning capability metadata.",
    },
    {
        "name": "health",
        "description": "Liveness and database readiness checks.",
    },
]


def create_application() -> FastAPI:
    configure_logging()
    settings.validate_production_safety()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        description=(
            "Backend API for tracking expenses, detecting micro-spending habits, "
            "generating savings insights, and supporting financial behavior analysis. "
            "Protected endpoints use JWT bearer authentication."
        ),
        openapi_tags=OPENAPI_TAGS,
    )

    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_application()
