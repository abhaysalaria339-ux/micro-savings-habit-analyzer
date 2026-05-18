from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.advanced import (
    AdvancedIntelligenceResponse,
    CalendarHeatmapDay,
    CalendarHeatmapResponse,
    HabitCoachRecommendation,
    RecurringExpenseCandidate,
    RecurringExpenseResponse,
    SpendingAnomaly,
    WeeklyFinancialHealthReport,
)


class AdvancedIntelligenceService:
    def __init__(self, expense_repository: ExpenseRepository) -> None:
        self.expense_repository = expense_repository

    async def get_advanced_intelligence(
        self,
        *,
        user_id: UUID,
        analysis_days: int = 90,
    ) -> AdvancedIntelligenceResponse:
        bounded_days = max(7, min(analysis_days, 180))
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=bounded_days - 1)

        expenses = await self.expense_repository.list_for_processing(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        recurring = self._detect_recurring_expenses(
            expenses=expenses,
            start_date=start_date,
            end_date=end_date,
        )
        heatmap = self._build_calendar_heatmap(
            expenses=expenses,
            start_date=start_date,
            end_date=end_date,
        )
        weekly_report = self._build_weekly_report(
            expenses=expenses,
            recurring=recurring,
            heatmap=heatmap,
            end_date=end_date,
        )
        anomalies = self._detect_anomalies(expenses=expenses, heatmap=heatmap)
        recommendations = self._build_coach_recommendations(
            weekly_report=weekly_report,
            recurring=recurring,
            anomalies=anomalies,
        )

        return AdvancedIntelligenceResponse(
            analysis_days=bounded_days,
            recurring_expenses=recurring,
            calendar_heatmap=heatmap,
            weekly_report=weekly_report,
            anomalies=anomalies,
            coach_recommendations=recommendations,
        )

    def _detect_recurring_expenses(
        self,
        *,
        expenses: list[Expense],
        start_date: datetime,
        end_date: datetime,
    ) -> RecurringExpenseResponse:
        grouped: dict[tuple[str, str | None], list[Expense]] = defaultdict(list)
        for expense in expenses:
            grouped[(expense.category, self._normalize_description(expense.description))].append(
                expense
            )

        analysis_days = max((end_date - start_date).days + 1, 1)
        candidates: list[RecurringExpenseCandidate] = []
        for (category, description), group in grouped.items():
            if len(group) < 3:
                continue

            sorted_group = sorted(group, key=lambda expense: expense.spent_at)
            first_spent_at = sorted_group[0].spent_at
            latest_spent_at = sorted_group[-1].spent_at
            average_days_between = self._average_days_between(
                first_spent_at=first_spent_at,
                latest_spent_at=latest_spent_at,
                occurrence_count=len(sorted_group),
            )
            total_amount = sum((expense.amount for expense in sorted_group), Decimal("0.00"))
            average_amount = total_amount / Decimal(len(sorted_group))
            projected_monthly_amount = self._project_monthly_amount(
                amount=total_amount,
                analysis_days=analysis_days,
            )
            confidence = self._classify_recurring_confidence(
                occurrence_count=len(sorted_group),
                average_days_between=average_days_between,
            )
            next_expected_at = None
            if average_days_between is not None:
                next_expected_at = latest_spent_at + timedelta(days=float(average_days_between))

            label = description or category
            candidates.append(
                RecurringExpenseCandidate(
                    category=category,
                    description=description,
                    occurrence_count=len(sorted_group),
                    average_amount=self._money(average_amount),
                    total_amount=self._money(total_amount),
                    average_days_between=average_days_between,
                    projected_monthly_amount=projected_monthly_amount,
                    confidence=confidence,
                    next_expected_at=next_expected_at,
                    recommendation=(
                        f"Review {label} before the next expected repeat and decide if it "
                        "should become a planned budget item."
                    ),
                )
            )

        candidates.sort(
            key=lambda candidate: (
                candidate.confidence == "high",
                candidate.projected_monthly_amount,
            ),
            reverse=True,
        )
        return RecurringExpenseResponse(
            start_date=start_date,
            end_date=end_date,
            candidates=candidates[:8],
        )

    def _build_calendar_heatmap(
        self,
        *,
        expenses: list[Expense],
        start_date: datetime,
        end_date: datetime,
    ) -> CalendarHeatmapResponse:
        totals: dict[datetime.date, Decimal] = defaultdict(lambda: Decimal("0.00"))
        counts: dict[datetime.date, int] = defaultdict(int)
        for expense in expenses:
            day = expense.spent_at.date()
            totals[day] += expense.amount
            counts[day] += 1

        max_daily_amount = max(totals.values(), default=Decimal("0.00"))
        days: list[CalendarHeatmapDay] = []
        current_day = start_date.date()
        while current_day <= end_date.date():
            total = self._money(totals[current_day])
            days.append(
                CalendarHeatmapDay(
                    day=current_day,
                    total_amount=total,
                    transaction_count=counts[current_day],
                    intensity=self._classify_day_intensity(
                        amount=total,
                        max_daily_amount=max_daily_amount,
                    ),
                )
            )
            current_day += timedelta(days=1)

        return CalendarHeatmapResponse(
            start_date=start_date,
            end_date=end_date,
            max_daily_amount=self._money(max_daily_amount),
            days=days,
        )

    def _build_weekly_report(
        self,
        *,
        expenses: list[Expense],
        recurring: RecurringExpenseResponse,
        heatmap: CalendarHeatmapResponse,
        end_date: datetime,
    ) -> WeeklyFinancialHealthReport:
        current_start = end_date - timedelta(days=6)
        previous_start = end_date - timedelta(days=13)
        previous_end = end_date - timedelta(days=7)

        current_expenses = [
            expense for expense in expenses if current_start <= expense.spent_at <= end_date
        ]
        previous_expenses = [
            expense
            for expense in expenses
            if previous_start <= expense.spent_at <= previous_end
        ]
        total_spend = self._sum_expenses(current_expenses)
        previous_total = self._sum_expenses(previous_expenses)
        top_category, top_category_amount = self._top_category(current_expenses)
        recurring_monthly_risk = sum(
            (
                candidate.projected_monthly_amount
                for candidate in recurring.candidates
                if candidate.confidence in {"medium", "high"}
            ),
            Decimal("0.00"),
        )
        high_spend_days = sum(1 for day in heatmap.days[-7:] if day.intensity == "high")
        change = self._percentage_change(current=total_spend, previous=previous_total)

        return WeeklyFinancialHealthReport(
            start_date=current_start,
            end_date=end_date,
            total_spend=self._money(total_spend),
            previous_total_spend=self._money(previous_total),
            spend_change_percentage=change,
            top_category=top_category,
            top_category_amount=self._money(top_category_amount),
            recurring_monthly_risk=self._money(recurring_monthly_risk),
            high_spend_days=high_spend_days,
            summary=self._build_weekly_summary(
                total_spend=total_spend,
                previous_total=previous_total,
                top_category=top_category,
            ),
            recommended_focus=self._build_weekly_focus(
                recurring=recurring,
                top_category=top_category,
                high_spend_days=high_spend_days,
            ),
        )

    def _detect_anomalies(
        self,
        *,
        expenses: list[Expense],
        heatmap: CalendarHeatmapResponse,
    ) -> list[SpendingAnomaly]:
        if not expenses:
            return []

        average_amount = self._sum_expenses(expenses) / Decimal(len(expenses))
        anomalies: list[SpendingAnomaly] = []
        for expense in expenses:
            if expense.amount >= average_amount * Decimal("3"):
                anomalies.append(
                    SpendingAnomaly(
                        anomaly_type="large_transaction",
                        severity="critical" if expense.amount >= average_amount * 5 else "warning",
                        title="Unusually large transaction",
                        description=(
                            f"{expense.category} spending is much higher than the average "
                            "transaction amount."
                        ),
                        detected_at=expense.spent_at,
                        amount=self._money(expense.amount),
                        category=expense.category,
                    )
                )

        for day in heatmap.days[-14:]:
            if day.intensity == "high":
                anomalies.append(
                    SpendingAnomaly(
                        anomaly_type="high_spend_day",
                        severity="warning",
                        title="High spending day detected",
                        description="This date stands out in the recent spending heatmap.",
                        detected_at=datetime.combine(day.day, datetime.min.time(), tzinfo=UTC),
                        amount=day.total_amount,
                    )
                )

        anomalies.sort(key=lambda anomaly: anomaly.amount, reverse=True)
        return anomalies[:6]

    def _build_coach_recommendations(
        self,
        *,
        weekly_report: WeeklyFinancialHealthReport,
        recurring: RecurringExpenseResponse,
        anomalies: list[SpendingAnomaly],
    ) -> list[HabitCoachRecommendation]:
        recommendations: list[HabitCoachRecommendation] = []
        top_recurring = recurring.candidates[0] if recurring.candidates else None
        if top_recurring is not None:
            label = top_recurring.description or top_recurring.category
            recommendations.append(
                HabitCoachRecommendation(
                    priority="high",
                    title=f"Review recurring {label}",
                    message=(
                        f"{label} may cost {top_recurring.projected_monthly_amount} "
                        "per month if it continues."
                    ),
                    action="Convert it into a planned budget item or pause it for seven days.",
                    estimated_monthly_impact=top_recurring.projected_monthly_amount,
                )
            )

        if weekly_report.top_category is not None:
            recommendations.append(
                HabitCoachRecommendation(
                    priority="medium",
                    title=f"Set a cap for {weekly_report.top_category}",
                    message=(
                        f"{weekly_report.top_category} is the strongest category this week."
                    ),
                    action="Set a 10% lower category cap for the next seven days.",
                    estimated_monthly_impact=self._money(
                        weekly_report.top_category_amount * Decimal("0.10")
                    ),
                )
            )

        if anomalies:
            recommendations.append(
                HabitCoachRecommendation(
                    priority="medium",
                    title="Check unusual spending",
                    message="One or more recent expenses were higher than your normal pattern.",
                    action="Review the largest unusual expense before repeating it.",
                    estimated_monthly_impact=anomalies[0].amount,
                )
            )

        if not recommendations:
            recommendations.append(
                HabitCoachRecommendation(
                    priority="low",
                    title="Keep tracking consistently",
                    message="No major advanced risk signals were found in this period.",
                    action="Continue daily tracking and move surplus into an active savings goal.",
                    estimated_monthly_impact=Decimal("0.00"),
                )
            )

        return recommendations[:4]

    def _normalize_description(self, description: str | None) -> str | None:
        if description is None:
            return None

        cleaned = " ".join(description.lower().strip().split())
        return cleaned or None

    def _average_days_between(
        self,
        *,
        first_spent_at: datetime,
        latest_spent_at: datetime,
        occurrence_count: int,
    ) -> Decimal | None:
        if occurrence_count < 2:
            return None

        elapsed_days = Decimal(str((latest_spent_at - first_spent_at).total_seconds()))
        average = elapsed_days / Decimal("86400") / Decimal(occurrence_count - 1)
        return average.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _classify_recurring_confidence(
        self,
        *,
        occurrence_count: int,
        average_days_between: Decimal | None,
    ) -> str:
        if average_days_between is not None and occurrence_count >= 5:
            if Decimal("0.50") <= average_days_between <= Decimal("14.00"):
                return "high"

        if occurrence_count >= 4:
            return "medium"

        return "low"

    def _classify_day_intensity(
        self,
        *,
        amount: Decimal,
        max_daily_amount: Decimal,
    ) -> str:
        if amount == Decimal("0.00") or max_daily_amount == Decimal("0.00"):
            return "none"

        ratio = amount / max_daily_amount
        if ratio >= Decimal("0.75"):
            return "high"

        if ratio >= Decimal("0.40"):
            return "medium"

        return "low"

    def _top_category(self, expenses: list[Expense]) -> tuple[str | None, Decimal]:
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        for expense in expenses:
            totals[expense.category] += expense.amount

        if not totals:
            return None, Decimal("0.00")

        category, amount = max(totals.items(), key=lambda item: item[1])
        return category, amount

    def _sum_expenses(self, expenses: list[Expense]) -> Decimal:
        return sum((expense.amount for expense in expenses), Decimal("0.00"))

    def _project_monthly_amount(self, *, amount: Decimal, analysis_days: int) -> Decimal:
        return self._money((amount / Decimal(analysis_days)) * Decimal("30"))

    def _percentage_change(self, *, current: Decimal, previous: Decimal) -> Decimal:
        if previous == Decimal("0.00"):
            return Decimal("0.00") if current == Decimal("0.00") else Decimal("100.00")

        return self._money(((current - previous) / previous) * Decimal("100"))

    def _build_weekly_summary(
        self,
        *,
        total_spend: Decimal,
        previous_total: Decimal,
        top_category: str | None,
    ) -> str:
        if total_spend == Decimal("0.00"):
            return "No expenses were found for the current week."

        comparison = "higher than" if total_spend > previous_total else "lower than or equal to"
        category_text = f" Top category: {top_category}." if top_category else ""
        return f"This week's spending is {comparison} the previous week.{category_text}"

    def _build_weekly_focus(
        self,
        *,
        recurring: RecurringExpenseResponse,
        top_category: str | None,
        high_spend_days: int,
    ) -> str:
        if recurring.candidates:
            label = recurring.candidates[0].description or recurring.candidates[0].category
            return f"Review recurring {label} before it repeats again."

        if high_spend_days > 0:
            return "Start by lowering the next high-spend day."

        if top_category:
            return f"Set a small weekly cap for {top_category}."

        return "Keep tracking daily expenses to improve future recommendations."

    def _money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
