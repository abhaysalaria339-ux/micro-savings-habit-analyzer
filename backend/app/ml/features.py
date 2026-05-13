from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from app.models.expense import Expense

MONEY_QUANTIZER = Decimal("0.01")
RATIO_QUANTIZER = Decimal("0.0001")
MICRO_EXPENSE_THRESHOLD = Decimal("100.00")


@dataclass(frozen=True)
class UserSpendingFeatureVector:
    transaction_count: int
    active_day_count: int
    total_spend: Decimal
    average_transaction_amount: Decimal
    average_daily_spend: Decimal
    micro_expense_count: int
    micro_expense_ratio: Decimal
    repeated_pattern_count: int
    unique_category_count: int
    top_category_spend_ratio: Decimal
    weekend_spend_ratio: Decimal
    food_and_snack_spend_ratio: Decimal
    subscription_spend_ratio: Decimal
    spending_frequency_per_day: Decimal
    first_half_spend: Decimal
    second_half_spend: Decimal
    spend_trend_ratio: Decimal

    def to_model_input(self) -> dict[str, float | int]:
        return {
            "transaction_count": self.transaction_count,
            "active_day_count": self.active_day_count,
            "total_spend": float(self.total_spend),
            "average_transaction_amount": float(self.average_transaction_amount),
            "average_daily_spend": float(self.average_daily_spend),
            "micro_expense_count": self.micro_expense_count,
            "micro_expense_ratio": float(self.micro_expense_ratio),
            "repeated_pattern_count": self.repeated_pattern_count,
            "unique_category_count": self.unique_category_count,
            "top_category_spend_ratio": float(self.top_category_spend_ratio),
            "weekend_spend_ratio": float(self.weekend_spend_ratio),
            "food_and_snack_spend_ratio": float(self.food_and_snack_spend_ratio),
            "subscription_spend_ratio": float(self.subscription_spend_ratio),
            "spending_frequency_per_day": float(self.spending_frequency_per_day),
            "first_half_spend": float(self.first_half_spend),
            "second_half_spend": float(self.second_half_spend),
            "spend_trend_ratio": float(self.spend_trend_ratio),
        }


class UserSpendingFeatureBuilder:
    def build(self, expenses: Iterable[Expense]) -> UserSpendingFeatureVector:
        expense_list = sorted(expenses, key=lambda expense: expense.spent_at)
        transaction_count = len(expense_list)

        if transaction_count == 0:
            return self._empty_vector()

        total_spend = self._sum_amounts(expense_list)
        active_days = {expense.spent_at.date() for expense in expense_list}
        analysis_days = self._analysis_day_count(active_days)
        category_totals = self._category_totals(expense_list)
        first_half, second_half = self._split_period_spend(expense_list)

        micro_expense_count = sum(
            1 for expense in expense_list if expense.amount <= MICRO_EXPENSE_THRESHOLD
        )
        weekend_spend = self._sum_amounts(
            expense for expense in expense_list if expense.spent_at.weekday() >= 5
        )
        food_and_snack_spend = sum(
            (
                amount
                for category, amount in category_totals.items()
                if category in {"coffee", "snacks", "food delivery"}
            ),
            Decimal("0.00"),
        )
        subscription_spend = category_totals.get("subscriptions", Decimal("0.00"))
        repeated_patterns = Counter(
            (expense.category.strip().lower(), (expense.description or "").strip().lower())
            for expense in expense_list
        )

        return UserSpendingFeatureVector(
            transaction_count=transaction_count,
            active_day_count=len(active_days),
            total_spend=self._quantize_money(total_spend),
            average_transaction_amount=self._safe_money_divide(
                total_spend,
                Decimal(transaction_count),
            ),
            average_daily_spend=self._safe_money_divide(total_spend, Decimal(analysis_days)),
            micro_expense_count=micro_expense_count,
            micro_expense_ratio=self._safe_ratio(
                Decimal(micro_expense_count),
                Decimal(transaction_count),
            ),
            repeated_pattern_count=sum(1 for count in repeated_patterns.values() if count >= 3),
            unique_category_count=len(category_totals),
            top_category_spend_ratio=self._safe_ratio(max(category_totals.values()), total_spend),
            weekend_spend_ratio=self._safe_ratio(weekend_spend, total_spend),
            food_and_snack_spend_ratio=self._safe_ratio(food_and_snack_spend, total_spend),
            subscription_spend_ratio=self._safe_ratio(subscription_spend, total_spend),
            spending_frequency_per_day=self._safe_ratio(
                Decimal(transaction_count),
                Decimal(analysis_days),
            ),
            first_half_spend=self._quantize_money(first_half),
            second_half_spend=self._quantize_money(second_half),
            spend_trend_ratio=self._calculate_trend_ratio(first_half, second_half),
        )

    def _empty_vector(self) -> UserSpendingFeatureVector:
        return UserSpendingFeatureVector(
            transaction_count=0,
            active_day_count=0,
            total_spend=Decimal("0.00"),
            average_transaction_amount=Decimal("0.00"),
            average_daily_spend=Decimal("0.00"),
            micro_expense_count=0,
            micro_expense_ratio=Decimal("0.0000"),
            repeated_pattern_count=0,
            unique_category_count=0,
            top_category_spend_ratio=Decimal("0.0000"),
            weekend_spend_ratio=Decimal("0.0000"),
            food_and_snack_spend_ratio=Decimal("0.0000"),
            subscription_spend_ratio=Decimal("0.0000"),
            spending_frequency_per_day=Decimal("0.0000"),
            first_half_spend=Decimal("0.00"),
            second_half_spend=Decimal("0.00"),
            spend_trend_ratio=Decimal("0.0000"),
        )

    def _category_totals(self, expenses: list[Expense]) -> dict[str, Decimal]:
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        for expense in expenses:
            totals[expense.category.strip().lower()] += expense.amount
        return dict(totals)

    def _split_period_spend(self, expenses: list[Expense]) -> tuple[Decimal, Decimal]:
        midpoint = expenses[0].spent_at + ((expenses[-1].spent_at - expenses[0].spent_at) / 2)
        first_half = self._sum_amounts(
            expense for expense in expenses if expense.spent_at <= midpoint
        )
        second_half = self._sum_amounts(
            expense for expense in expenses if expense.spent_at > midpoint
        )
        return first_half, second_half

    def _calculate_trend_ratio(self, first_half: Decimal, second_half: Decimal) -> Decimal:
        if first_half == Decimal("0.00") and second_half == Decimal("0.00"):
            return Decimal("0.0000")
        if first_half == Decimal("0.00"):
            return Decimal("1.0000")
        return self._safe_ratio(second_half - first_half, first_half)

    def _analysis_day_count(self, active_days: set[date]) -> int:
        if not active_days:
            return 0
        return max(1, (max(active_days) - min(active_days)).days + 1)

    def _sum_amounts(self, expenses: Iterable[Expense]) -> Decimal:
        return sum((expense.amount for expense in expenses), Decimal("0.00"))

    def _safe_money_divide(self, numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == Decimal("0"):
            return Decimal("0.00")
        return self._quantize_money(numerator / denominator)

    def _safe_ratio(self, numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == Decimal("0"):
            return Decimal("0.0000")
        return (numerator / denominator).quantize(RATIO_QUANTIZER, rounding=ROUND_HALF_UP)

    def _quantize_money(self, amount: Decimal) -> Decimal:
        return amount.quantize(MONEY_QUANTIZER, rounding=ROUND_HALF_UP)
