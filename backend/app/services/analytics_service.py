from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal
from uuid import UUID

from app.repositories.expense_repository import ExpenseRepository
from app.schemas.analytics import (
    BehaviorScoreFactor,
    CategorySpendingSummary,
    FinancialBehaviorScore,
    MicroExpenseAnalysis,
    MicroExpensePattern,
    MoneyLeakAnalysis,
    MoneyLeakPattern,
    RepeatedSpendingAnalysis,
    RepeatedSpendingPattern,
    SpendingSummary,
    SpendingTrendAnalysis,
    SpendingTrendPoint,
    WeekdayWeekendAnalysis,
    WeekdayWeekendSpendingSegment,
)


class AnalyticsService:
    def __init__(self, expense_repository: ExpenseRepository) -> None:
        self.expense_repository = expense_repository

    async def get_spending_summary(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> SpendingSummary:
        total_amount, transaction_count, average_amount = (
            await self.expense_repository.get_spending_totals(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
            )
        )
        category_rows = await self.expense_repository.get_category_spending_totals(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        categories = [
            CategorySpendingSummary(
                category=category,
                total_amount=category_total,
                transaction_count=category_count,
                percentage_of_total=self._calculate_percentage(category_total, total_amount),
            )
            for category, category_total, category_count in category_rows
        ]

        return SpendingSummary(
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
            transaction_count=transaction_count,
            average_expense_amount=average_amount,
            categories=categories,
        )

    async def detect_micro_expenses(
        self,
        *,
        user_id: UUID,
        max_expense_amount: Decimal,
        min_occurrences: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> MicroExpenseAnalysis:
        resolved_start_date, resolved_end_date = self._resolve_analysis_period(
            start_date=start_date,
            end_date=end_date,
        )
        rows = await self.expense_repository.get_micro_expense_patterns(
            user_id=user_id,
            max_expense_amount=max_expense_amount,
            min_occurrences=min_occurrences,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

        analysis_days = max((resolved_end_date - resolved_start_date).days + 1, 1)
        total_micro_expense_amount = Decimal("0.00")
        patterns: list[MicroExpensePattern] = []

        for category, description, count, average_amount, total_amount, latest_spent_at in rows:
            total_micro_expense_amount += total_amount
            patterns.append(
                MicroExpensePattern(
                    category=category,
                    description=description,
                    occurrence_count=count,
                    average_amount=self._quantize_money(average_amount),
                    total_amount=self._quantize_money(total_amount),
                    projected_monthly_amount=self._project_monthly_amount(
                        amount=total_amount,
                        analysis_days=analysis_days,
                    ),
                    latest_spent_at=latest_spent_at,
                )
            )

        return MicroExpenseAnalysis(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            max_expense_amount=max_expense_amount,
            min_occurrences=min_occurrences,
            total_micro_expense_amount=self._quantize_money(total_micro_expense_amount),
            patterns=patterns,
        )

    async def compare_weekday_weekend_spending(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> WeekdayWeekendAnalysis:
        resolved_start_date, resolved_end_date = self._resolve_analysis_period(
            start_date=start_date,
            end_date=end_date,
        )
        rows = await self.expense_repository.get_weekday_weekend_spending(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

        totals_by_period = {
            period: (total_amount, transaction_count, average_amount)
            for period, total_amount, transaction_count, average_amount in rows
        }
        total_amount = sum(
            (amount for amount, _, _ in totals_by_period.values()),
            Decimal("0.00"),
        )
        weekday = self._build_weekday_weekend_segment(
            period_type="weekday",
            values=totals_by_period.get("weekday"),
            total_amount=total_amount,
        )
        weekend = self._build_weekday_weekend_segment(
            period_type="weekend",
            values=totals_by_period.get("weekend"),
            total_amount=total_amount,
        )
        higher_spending_period = self._get_higher_spending_period(
            weekday_amount=weekday.total_amount,
            weekend_amount=weekend.total_amount,
        )

        return WeekdayWeekendAnalysis(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            total_amount=self._quantize_money(total_amount),
            weekday=weekday,
            weekend=weekend,
            higher_spending_period=higher_spending_period,
            difference_amount=self._quantize_money(
                abs(weekday.total_amount - weekend.total_amount)
            ),
        )

    async def detect_repeated_spending(
        self,
        *,
        user_id: UUID,
        min_occurrences: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> RepeatedSpendingAnalysis:
        resolved_start_date, resolved_end_date = self._resolve_analysis_period(
            start_date=start_date,
            end_date=end_date,
        )
        rows = await self.expense_repository.get_repeated_spending_patterns(
            user_id=user_id,
            min_occurrences=min_occurrences,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

        total_repeated_amount = Decimal("0.00")
        patterns: list[RepeatedSpendingPattern] = []

        for (
            category,
            description,
            occurrence_count,
            total_amount,
            average_amount,
            first_spent_at,
            latest_spent_at,
        ) in rows:
            total_repeated_amount += total_amount
            patterns.append(
                RepeatedSpendingPattern(
                    category=category,
                    description=description,
                    occurrence_count=occurrence_count,
                    total_amount=self._quantize_money(total_amount),
                    average_amount=self._quantize_money(average_amount),
                    first_spent_at=first_spent_at,
                    latest_spent_at=latest_spent_at,
                    average_days_between=self._calculate_average_days_between(
                        first_spent_at=first_spent_at,
                        latest_spent_at=latest_spent_at,
                        occurrence_count=occurrence_count,
                    ),
                )
            )

        return RepeatedSpendingAnalysis(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            min_occurrences=min_occurrences,
            total_repeated_amount=self._quantize_money(total_repeated_amount),
            patterns=patterns,
        )

    async def calculate_financial_behavior_score(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> FinancialBehaviorScore:
        resolved_start_date, resolved_end_date = self._resolve_analysis_period(
            start_date=start_date,
            end_date=end_date,
        )
        spending_summary = await self.get_spending_summary(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        micro_expenses = await self.detect_micro_expenses(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            max_expense_amount=Decimal("100.00"),
            min_occurrences=3,
        )
        repeated_spending = await self.detect_repeated_spending(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            min_occurrences=3,
        )
        weekday_weekend = await self.compare_weekday_weekend_spending(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

        score = 75
        factors: list[BehaviorScoreFactor] = []

        if spending_summary.transaction_count == 0:
            return FinancialBehaviorScore(
                start_date=resolved_start_date,
                end_date=resolved_end_date,
                score=50,
                classification="Neutral",
                total_amount=Decimal("0.00"),
                transaction_count=0,
                factors=[
                    BehaviorScoreFactor(
                        name="insufficient_data",
                        impact=0,
                        message="No expenses were found for the selected period.",
                    )
                ],
            )

        top_category = spending_summary.categories[0] if spending_summary.categories else None
        if top_category is not None and top_category.percentage_of_total >= Decimal("50.00"):
            score -= 10
            factors.append(
                BehaviorScoreFactor(
                    name="category_concentration",
                    impact=-10,
                    message=f"{top_category.category} dominates selected-period spending.",
                )
            )
        elif top_category is not None and top_category.percentage_of_total >= Decimal("40.00"):
            score -= 5
            factors.append(
                BehaviorScoreFactor(
                    name="category_concentration",
                    impact=-5,
                    message=f"{top_category.category} is a high-share spending category.",
                )
            )

        micro_expense_ratio = self._calculate_percentage(
            micro_expenses.total_micro_expense_amount,
            spending_summary.total_amount,
        )
        if micro_expense_ratio >= Decimal("15.00"):
            score -= 10
            factors.append(
                BehaviorScoreFactor(
                    name="micro_expense_load",
                    impact=-10,
                    message="Small repeated expenses form a significant share of spending.",
                )
            )
        elif micro_expense_ratio >= Decimal("8.00"):
            score -= 5
            factors.append(
                BehaviorScoreFactor(
                    name="micro_expense_load",
                    impact=-5,
                    message="Small repeated expenses are noticeable in this period.",
                )
            )

        repeated_spending_ratio = self._calculate_percentage(
            repeated_spending.total_repeated_amount,
            spending_summary.total_amount,
        )
        if repeated_spending_ratio >= Decimal("40.00"):
            score -= 15
            factors.append(
                BehaviorScoreFactor(
                    name="repeated_spending_load",
                    impact=-15,
                    message="Repeated spending patterns account for a large share of spending.",
                )
            )
        elif repeated_spending_ratio >= Decimal("25.00"):
            score -= 8
            factors.append(
                BehaviorScoreFactor(
                    name="repeated_spending_load",
                    impact=-8,
                    message="Repeated spending patterns are materially affecting spending.",
                )
            )

        if weekday_weekend.weekend.percentage_of_total >= Decimal("45.00"):
            score -= 5
            factors.append(
                BehaviorScoreFactor(
                    name="weekend_spending_bias",
                    impact=-5,
                    message="Weekend spending is unusually high for the selected period.",
                )
            )

        if not factors:
            score += 10
            factors.append(
                BehaviorScoreFactor(
                    name="stable_spending_pattern",
                    impact=10,
                    message="No major concentration or repeated spending risks were detected.",
                )
            )

        score = max(0, min(score, 100))

        return FinancialBehaviorScore(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            score=score,
            classification=self._classify_behavior_score(score),
            total_amount=self._quantize_money(spending_summary.total_amount),
            transaction_count=spending_summary.transaction_count,
            factors=factors,
        )

    async def detect_money_leaks(
        self,
        *,
        user_id: UUID,
        min_occurrences: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> MoneyLeakAnalysis:
        resolved_start_date, resolved_end_date = self._resolve_analysis_period(
            start_date=start_date,
            end_date=end_date,
        )
        repeated_spending = await self.detect_repeated_spending(
            user_id=user_id,
            min_occurrences=min_occurrences,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

        analysis_days = max((resolved_end_date - resolved_start_date).days + 1, 1)
        patterns: list[MoneyLeakPattern] = []

        for pattern in repeated_spending.patterns:
            if pattern.average_days_between is None:
                continue

            leak_risk = self._classify_money_leak_risk(
                average_days_between=pattern.average_days_between,
                total_amount=pattern.total_amount,
            )
            if leak_risk == "low" and pattern.total_amount < Decimal("500.00"):
                continue

            patterns.append(
                MoneyLeakPattern(
                    category=pattern.category,
                    description=pattern.description,
                    occurrence_count=pattern.occurrence_count,
                    total_amount=pattern.total_amount,
                    average_amount=pattern.average_amount,
                    projected_monthly_leak=self._project_monthly_amount(
                        amount=pattern.total_amount,
                        analysis_days=analysis_days,
                    ),
                    average_days_between=pattern.average_days_between,
                    leak_risk=leak_risk,
                    reason=self._build_money_leak_reason(
                        pattern_description=pattern.description,
                        category=pattern.category,
                        average_days_between=pattern.average_days_between,
                    ),
                )
            )

        total_leak_amount = sum(
            (pattern.total_amount for pattern in patterns),
            Decimal("0.00"),
        )
        projected_monthly_leak = sum(
            (pattern.projected_monthly_leak for pattern in patterns),
            Decimal("0.00"),
        )

        return MoneyLeakAnalysis(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            total_leak_amount=self._quantize_money(total_leak_amount),
            projected_monthly_leak=self._quantize_money(projected_monthly_leak),
            patterns=patterns,
        )

    async def analyze_spending_trends(
        self,
        *,
        user_id: UUID,
        interval: Literal["daily", "weekly", "monthly"],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> SpendingTrendAnalysis:
        resolved_start_date, resolved_end_date = self._resolve_analysis_period(
            start_date=start_date,
            end_date=end_date,
        )
        rows = await self.expense_repository.get_spending_trends(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            interval=self._to_postgres_trend_interval(interval),
        )
        points = [
            SpendingTrendPoint(
                period_start=period_start,
                total_amount=self._quantize_money(total_amount),
                transaction_count=transaction_count,
                average_expense_amount=self._quantize_money(average_amount),
            )
            for period_start, total_amount, transaction_count, average_amount in rows
        ]
        total_amount = sum(
            (point.total_amount for point in points),
            Decimal("0.00"),
        )

        return SpendingTrendAnalysis(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            interval=interval,
            total_amount=self._quantize_money(total_amount),
            points=points,
        )

    def _calculate_percentage(self, amount: Decimal, total_amount: Decimal) -> Decimal:
        if total_amount == Decimal("0"):
            return Decimal("0.00")

        return ((amount / total_amount) * Decimal("100")).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def _resolve_analysis_period(
        self,
        *,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        resolved_start_date = self._normalize_datetime(start_date) or now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        resolved_end_date = self._normalize_datetime(end_date) or now
        return resolved_start_date, resolved_end_date

    def _normalize_datetime(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=UTC)

        return value

    def _project_monthly_amount(self, *, amount: Decimal, analysis_days: int) -> Decimal:
        projected_amount = (amount / Decimal(analysis_days)) * Decimal("30")
        return self._quantize_money(projected_amount)

    def _quantize_money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _build_weekday_weekend_segment(
        self,
        *,
        period_type: str,
        values: tuple[Decimal, int, Decimal] | None,
        total_amount: Decimal,
    ) -> WeekdayWeekendSpendingSegment:
        amount, transaction_count, average_amount = values or (
            Decimal("0.00"),
            0,
            Decimal("0.00"),
        )

        return WeekdayWeekendSpendingSegment(
            period_type=period_type,
            total_amount=self._quantize_money(amount),
            transaction_count=transaction_count,
            average_expense_amount=self._quantize_money(average_amount),
            percentage_of_total=self._calculate_percentage(amount, total_amount),
        )

    def _get_higher_spending_period(
        self,
        *,
        weekday_amount: Decimal,
        weekend_amount: Decimal,
    ) -> str | None:
        if weekday_amount == weekend_amount:
            return None

        if weekday_amount > weekend_amount:
            return "weekday"

        return "weekend"

    def _calculate_average_days_between(
        self,
        *,
        first_spent_at: datetime,
        latest_spent_at: datetime,
        occurrence_count: int,
    ) -> Decimal | None:
        if occurrence_count < 2:
            return None

        elapsed_days = Decimal(str((latest_spent_at - first_spent_at).total_seconds()))
        average_days = elapsed_days / Decimal("86400") / Decimal(occurrence_count - 1)
        return average_days.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _classify_behavior_score(self, score: int) -> Literal["Saver", "Neutral", "Spender"]:
        if score >= 70:
            return "Saver"

        if score >= 45:
            return "Neutral"

        return "Spender"

    def _classify_money_leak_risk(
        self,
        *,
        average_days_between: Decimal,
        total_amount: Decimal,
    ) -> Literal["low", "medium", "high"]:
        if average_days_between <= Decimal("10.00") and total_amount >= Decimal("1000.00"):
            return "high"

        if average_days_between <= Decimal("15.00") or total_amount >= Decimal("750.00"):
            return "medium"

        return "low"

    def _build_money_leak_reason(
        self,
        *,
        pattern_description: str | None,
        category: str,
        average_days_between: Decimal,
    ) -> str:
        label = pattern_description or category
        return f"{label} repeats about every {average_days_between} days."

    def _to_postgres_trend_interval(
        self,
        interval: Literal["daily", "weekly", "monthly"],
    ) -> str:
        if interval == "daily":
            return "day"

        if interval == "weekly":
            return "week"

        return "month"
