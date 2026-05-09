from decimal import Decimal

from app.schemas.pipeline import PipelineCategoryAggregate, PipelineFeatureSet


class PipelineInsightGeneration:
    def generate(
        self,
        *,
        features: PipelineFeatureSet,
        category_aggregates: list[PipelineCategoryAggregate],
    ) -> list[str]:
        insights: list[str] = []

        if features.transaction_count == 0:
            return ["No expenses were available for the selected period."]

        if features.micro_expense_count >= 3:
            insights.append("Small expenses appear frequently in this period.")

        if features.repeated_pattern_count > 0:
            insights.append("Repeated spending patterns are present in the cleaned data.")

        top_category = category_aggregates[0] if category_aggregates else None
        if top_category is not None and features.total_amount > Decimal("0.00"):
            category_share = (top_category.total_amount / features.total_amount) * Decimal("100")
            if category_share >= Decimal("40.00"):
                insights.append(f"{top_category.category} is the dominant spending category.")

        return insights
