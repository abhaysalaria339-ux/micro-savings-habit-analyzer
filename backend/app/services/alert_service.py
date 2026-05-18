from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.alert import SpendingAlert, SpendingAlertsResponse
from app.services.analytics_service import AnalyticsService
from app.services.budget_service import BudgetService


class AlertService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        budget_repository: BudgetRepository | None = None,
    ) -> None:
        self.analytics_service = AnalyticsService(expense_repository)
        self.budget_service = (
            BudgetService(budget_repository, expense_repository)
            if budget_repository is not None
            else None
        )

    async def get_spending_alerts(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> SpendingAlertsResponse:
        resolved_start_date, resolved_end_date = self._resolve_period(
            start_date=start_date,
            end_date=end_date,
        )
        behavior_score = await self.analytics_service.calculate_financial_behavior_score(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        micro_expenses = await self.analytics_service.detect_micro_expenses(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            max_expense_amount=Decimal("100.00"),
            min_occurrences=3,
        )
        repeated_spending = await self.analytics_service.detect_repeated_spending(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            min_occurrences=3,
        )
        weekday_weekend = await self.analytics_service.compare_weekday_weekend_spending(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

        alerts = [
            *self._build_behavior_score_alerts(behavior_score),
            *self._build_micro_expense_alerts(micro_expenses.patterns[:2]),
            *self._build_repeated_spending_alerts(repeated_spending.patterns[:2]),
            *self._build_weekend_spending_alerts(weekday_weekend),
        ]
        if self.budget_service is not None:
            budgets = await self.budget_service.list_budgets(user_id=user_id)
            alerts.extend(self._build_budget_alerts(budgets))

        return SpendingAlertsResponse(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            alerts=alerts,
        )

    def _build_behavior_score_alerts(self, behavior_score) -> list[SpendingAlert]:
        if behavior_score.classification != "Spender":
            return []

        return [
            SpendingAlert(
                alert_type="behavior_score",
                severity="critical",
                title="Spending pattern needs attention",
                message=f"Your behavior score is {behavior_score.score}.",
                nudge="Review your top repeated spending pattern before your next purchase.",
                estimated_monthly_impact=Decimal("0.00"),
            )
        ]

    def _build_micro_expense_alerts(self, patterns) -> list[SpendingAlert]:
        alerts: list[SpendingAlert] = []

        for pattern in patterns:
            target = pattern.description or pattern.category
            alerts.append(
                SpendingAlert(
                    alert_type="micro_expense",
                    severity="warning",
                    title=f"Small {pattern.category} purchases are adding up",
                    message=(
                        f"{target} appears {pattern.occurrence_count} times in this period."
                    ),
                    nudge="Try skipping the next occurrence and save the amount immediately.",
                    estimated_monthly_impact=pattern.projected_monthly_amount,
                )
            )

        return alerts

    def _build_budget_alerts(self, budgets) -> list[SpendingAlert]:
        alerts: list[SpendingAlert] = []

        for budget in budgets:
            if budget.usage_percentage < Decimal("80.00"):
                continue

            is_over_budget = budget.status == "over"
            alerts.append(
                SpendingAlert(
                    alert_type="budget_breach",
                    severity="critical" if is_over_budget else "warning",
                    title=f"{budget.category} budget needs attention",
                    message=(
                        f"{budget.category} is at {budget.usage_percentage}% of its "
                        "monthly budget."
                    ),
                    nudge="Pause non-essential spending in this category until next month.",
                    estimated_monthly_impact=(
                        budget.spent_amount - budget.monthly_limit
                        if is_over_budget
                        else budget.remaining_amount
                    ),
                )
            )

        return alerts[:3]

    def _build_repeated_spending_alerts(self, patterns) -> list[SpendingAlert]:
        alerts: list[SpendingAlert] = []

        for pattern in patterns:
            target = pattern.description or pattern.category
            alerts.append(
                SpendingAlert(
                    alert_type="repeated_spending",
                    severity="info",
                    title=f"Repeated {pattern.category} pattern detected",
                    message=f"{target} has repeated {pattern.occurrence_count} times.",
                    nudge="Set a limit before the next expected repeat purchase.",
                    estimated_monthly_impact=pattern.total_amount,
                )
            )

        return alerts

    def _build_weekend_spending_alerts(self, weekday_weekend) -> list[SpendingAlert]:
        if weekday_weekend.weekend.percentage_of_total < Decimal("45.00"):
            return []

        return [
            SpendingAlert(
                alert_type="weekend_spending",
                severity="warning",
                title="Weekend spending is elevated",
                message=(
                    f"Weekend spending is {weekday_weekend.weekend.percentage_of_total}% "
                    "of selected-period spending."
                ),
                nudge="Set a weekend spending cap before Friday evening.",
                estimated_monthly_impact=weekday_weekend.weekend.total_amount,
            )
        ]

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
