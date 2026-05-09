from datetime import UTC
from decimal import ROUND_HALF_UP, Decimal

from app.models.expense import Expense
from app.schemas.pipeline import ProcessedExpense


class ExpenseCleaningPipeline:
    def clean(self, expenses: list[Expense]) -> list[ProcessedExpense]:
        cleaned_expenses: list[ProcessedExpense] = []

        for expense in expenses:
            if expense.amount <= Decimal("0"):
                continue

            cleaned_expenses.append(
                ProcessedExpense(
                    amount=self._quantize_money(expense.amount),
                    category=expense.category.strip().title(),
                    description=expense.description.strip() if expense.description else None,
                    spent_at=self._normalize_datetime(expense.spent_at),
                )
            )

        return cleaned_expenses

    def _normalize_datetime(self, value):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=UTC)

        return value

    def _quantize_money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
