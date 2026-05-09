from datetime import UTC, datetime
from uuid import UUID

from app.repositories.expense_repository import ExpenseRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.dashboard import DashboardResponse
from app.services.alert_service import AlertService
from app.services.analytics_service import AnalyticsService
from app.services.goal_service import GoalService
from app.services.insight_service import InsightService


class DashboardService:
    def __init__(
        self,
        *,
        expense_repository: ExpenseRepository,
        goal_repository: GoalRepository,
    ) -> None:
        self.analytics_service = AnalyticsService(expense_repository)
        self.insight_service = InsightService(expense_repository)
        self.alert_service = AlertService(expense_repository)
        self.goal_service = GoalService(goal_repository)

    async def get_dashboard(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> DashboardResponse:
        resolved_start_date, resolved_end_date = self._resolve_period(
            start_date=start_date,
            end_date=end_date,
        )
        spending_summary = await self.analytics_service.get_spending_summary(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        spending_trends = await self.analytics_service.analyze_spending_trends(
            user_id=user_id,
            interval="daily",
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        savings_insights = await self.insight_service.get_savings_insights(
            user_id=user_id,
            period="monthly",
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        behavior_score = await self.analytics_service.calculate_financial_behavior_score(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        alerts = await self.alert_service.get_spending_alerts(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        money_leaks = await self.analytics_service.detect_money_leaks(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            min_occurrences=3,
        )
        goals = await self.goal_service.list_goals(user_id=user_id, is_completed=None)

        return DashboardResponse(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            spending_summary=spending_summary,
            spending_trends=spending_trends,
            savings_opportunities=savings_insights.insights,
            behavior_score=behavior_score,
            alerts=alerts.alerts,
            money_leaks=money_leaks,
            goals=goals,
        )

    def _resolve_period(
        self,
        *,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        resolved_start_date = start_date or now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        resolved_end_date = end_date or now
        return (
            self._normalize_datetime(resolved_start_date),
            self._normalize_datetime(resolved_end_date),
        )

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=UTC)

        return value
