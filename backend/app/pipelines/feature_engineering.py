from collections import Counter
from decimal import ROUND_HALF_UP, Decimal

from app.schemas.pipeline import PipelineFeatureSet, ProcessedExpense


class ExpenseFeatureEngineeringPipeline:
    def build_features(self, expenses: list[ProcessedExpense]) -> PipelineFeatureSet:
        transaction_count = len(expenses)
        total_amount = sum((expense.amount for expense in expenses), Decimal("0.00"))
        average_amount = (
            total_amount / Decimal(transaction_count)
            if transaction_count > 0
            else Decimal("0.00")
        )
        repeated_patterns = Counter(
            (expense.category, expense.description)
            for expense in expenses
        )

        return PipelineFeatureSet(
            transaction_count=transaction_count,
            total_amount=self._quantize_money(total_amount),
            average_expense_amount=self._quantize_money(average_amount),
            unique_category_count=len({expense.category for expense in expenses}),
            micro_expense_count=sum(
                1 for expense in expenses if expense.amount <= Decimal("100.00")
            ),
            repeated_pattern_count=sum(1 for count in repeated_patterns.values() if count >= 3),
        )

    def _quantize_money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
