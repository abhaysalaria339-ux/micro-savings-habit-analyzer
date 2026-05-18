import calendar
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.repositories.expense_repository import ExpenseRepository
from app.repositories.settings_repository import SettingsRepository
from app.schemas.forecast import SpendingForecastResponse
from app.services.settings_service import SettingsService


class ForecastService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        settings_repository: SettingsRepository,
    ) -> None:
        self.expense_repository = expense_repository
        self.settings_service = SettingsService(settings_repository)

    async def get_month_end_forecast(self, *, user_id: UUID) -> SpendingForecastResponse:
        now = datetime.now(UTC)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total, count, _average = await self.expense_repository.get_spending_totals(
            user_id=user_id,
            start_date=period_start,
            end_date=now,
        )
        elapsed_days = max(now.day, 1)
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        daily_average = total / Decimal(elapsed_days)
        projection = daily_average * Decimal(days_in_month)
        settings = await self.settings_service.get_settings(user_id=user_id)
        target_spend = Decimal("0.00")
        if settings.monthly_income is not None:
            target_spend = settings.monthly_income * (
                (Decimal("100.00") - settings.savings_target_percentage) / Decimal("100.00")
            )
        projected_savings_gap = max(projection - target_spend, Decimal("0.00"))
        confidence = "high" if count >= 20 else "medium" if count >= 8 else "low"

        return SpendingForecastResponse(
            period_start=period_start,
            period_end=now,
            month_end_projection=self._money(projection),
            current_month_spend=self._money(total),
            daily_average=self._money(daily_average),
            projected_savings_gap=self._money(projected_savings_gap),
            confidence=confidence,
            summary=f"At the current pace, month-end spend may reach {self._money(projection)}.",
        )

    def _money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
