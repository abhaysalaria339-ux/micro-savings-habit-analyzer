from fastapi import APIRouter

from app.api.openapi import COMMON_ERROR_RESPONSES
from app.api.v1.endpoints import (
    account,
    advanced,
    alerts,
    analytics,
    auth,
    backup,
    budgets,
    dashboard,
    demo,
    expenses,
    forecast,
    goals,
    health,
    insights,
    ml,
    notifications,
    reports,
    settings,
    simulator,
    subscriptions,
)

api_router = APIRouter(responses=COMMON_ERROR_RESPONSES)
api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(advanced.router, prefix="/advanced", tags=["advanced"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["forecast"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(simulator.router, prefix="/simulator", tags=["simulator"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
