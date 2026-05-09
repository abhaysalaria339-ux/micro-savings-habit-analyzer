from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal
from uuid import UUID

from app.repositories.expense_repository import ExpenseRepository
from app.schemas.insight import SavingsInsight, SavingsInsightsResponse
from app.services.analytics_service import AnalyticsService


class InsightService:
    def __init__(self, expense_repository: ExpenseRepository) -> None:
        self.analytics_service = AnalyticsService(expense_repository)

    async def get_savings_insights(
        self,
        *,
        user_id: UUID,
        period: Literal["weekly", "monthly"],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> SavingsInsightsResponse:
        resolved_start_date, resolved_end_date = self._resolve_period(
            period=period,
            start_date=start_date,
            end_date=end_date,
        )
        spending_summary = await self.analytics_service.get_spending_summary(
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

        insights = [
            *self._build_micro_expense_insights(micro_expenses.patterns[:3]),
            *self._build_repeated_spending_insights(repeated_spending.patterns[:3]),
            *self._build_category_concentration_insights(spending_summary.categories[:1]),
        ]
        total_estimated_monthly_savings = sum(
            (insight.estimated_monthly_savings for insight in insights),
            Decimal("0.00"),
        )

        return SavingsInsightsResponse(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            period=period,
            total_estimated_monthly_savings=self._quantize_money(
                total_estimated_monthly_savings
            ),
            insights=insights,
        )

    def _build_micro_expense_insights(self, patterns) -> list[SavingsInsight]:
        insights: list[SavingsInsight] = []

        for pattern in patterns:
            target = pattern.description or pattern.category
            estimated_savings = pattern.projected_monthly_amount * Decimal("0.50")
            insights.append(
                SavingsInsight(
                    insight_type="micro_expense",
                    title=f"Reduce repeated {pattern.category} spending",
                    message=(
                        f"{target} appeared {pattern.occurrence_count} times and totals "
                        f"{pattern.total_amount} in the selected period."
                    ),
                    action="Try cutting this pattern by half for the next month.",
                    estimated_monthly_savings=self._quantize_money(estimated_savings),
                )
            )

        return insights

    def _build_repeated_spending_insights(self, patterns) -> list[SavingsInsight]:
        insights: list[SavingsInsight] = []

        for pattern in patterns:
            if pattern.average_days_between is None:
                continue

            target = pattern.description or pattern.category
            estimated_savings = pattern.average_amount
            insights.append(
                SavingsInsight(
                    insight_type="repeated_spending",
                    title=f"Pause one {pattern.category} purchase",
                    message=(
                        f"{target} repeats about every {pattern.average_days_between} days."
                    ),
                    action="Skip one occurrence this month and move that amount to savings.",
                    estimated_monthly_savings=self._quantize_money(estimated_savings),
                )
            )

        return insights

    def _build_category_concentration_insights(self, categories) -> list[SavingsInsight]:
        insights: list[SavingsInsight] = []

        for category in categories:
            if category.percentage_of_total < Decimal("40.00"):
                continue

            estimated_savings = category.total_amount * Decimal("0.10")
            insights.append(
                SavingsInsight(
                    insight_type="category_concentration",
                    title=f"Set a cap for {category.category}",
                    message=(
                        f"{category.category} represents {category.percentage_of_total}% "
                        "of selected-period spending."
                    ),
                    action="Set a 10% lower spending cap for this category next month.",
                    estimated_monthly_savings=self._quantize_money(estimated_savings),
                )
            )

        return insights

    def _resolve_period(
        self,
        *,
        period: Literal["weekly", "monthly"],
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> tuple[datetime, datetime]:
        if start_date is not None and end_date is not None:
            return self._normalize_datetime(start_date), self._normalize_datetime(end_date)

        now = datetime.now(UTC)
        if period == "weekly":
            start_of_week = now - timedelta(days=now.weekday())
            return (
                start_of_week.replace(hour=0, minute=0, second=0, microsecond=0),
                now,
            )

        return (
            now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            now,
        )

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=UTC)

        return value

    def _quantize_money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
