from decimal import Decimal

from app.schemas.pipeline import PipelineCategoryAggregate, ProcessedExpense


class ExpenseAggregationPipeline:
    def aggregate_by_category(
        self,
        expenses: list[ProcessedExpense],
    ) -> list[PipelineCategoryAggregate]:
        totals_by_category: dict[str, tuple[Decimal, int]] = {}

        for expense in expenses:
            current_total, current_count = totals_by_category.get(
                expense.category,
                (Decimal("0.00"), 0),
            )
            totals_by_category[expense.category] = (
                current_total + expense.amount,
                current_count + 1,
            )

        return [
            PipelineCategoryAggregate(
                category=category,
                total_amount=total_amount,
                transaction_count=transaction_count,
            )
            for category, (total_amount, transaction_count) in sorted(
                totals_by_category.items(),
                key=lambda item: item[1][0],
                reverse=True,
            )
        ]
