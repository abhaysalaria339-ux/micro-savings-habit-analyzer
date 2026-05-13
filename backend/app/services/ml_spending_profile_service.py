from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.ml.clustering import SpendingProfileClusteringModel
from app.ml.features import UserSpendingFeatureBuilder
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.ml import MLFeatureSnapshot, MLSpendingProfileResponse


class MLSpendingProfileService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        feature_builder: UserSpendingFeatureBuilder | None = None,
        clustering_model: SpendingProfileClusteringModel | None = None,
    ) -> None:
        self.expense_repository = expense_repository
        self.feature_builder = feature_builder or UserSpendingFeatureBuilder()
        self.clustering_model = clustering_model or SpendingProfileClusteringModel()

    async def get_spending_profile(
        self,
        *,
        user_id: UUID,
        analysis_days: int,
    ) -> MLSpendingProfileResponse:
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=analysis_days)
        expenses = await self.expense_repository.list_for_processing(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        features = self.feature_builder.build(expenses)
        prediction = self.clustering_model.predict(features)

        return MLSpendingProfileResponse(
            profile_id=prediction.cluster_id,
            profile_label=prediction.profile_label,
            confidence=prediction.confidence,
            summary=prediction.summary,
            reasons=prediction.reasons,
            recommendations=prediction.recommendations,
            analysis_days=analysis_days,
            transaction_count=features.transaction_count,
            features=MLFeatureSnapshot(
                total_spend=features.total_spend,
                average_transaction_amount=features.average_transaction_amount,
                average_daily_spend=features.average_daily_spend,
                micro_expense_ratio=features.micro_expense_ratio,
                repeated_pattern_count=features.repeated_pattern_count,
                unique_category_count=features.unique_category_count,
                top_category_spend_ratio=features.top_category_spend_ratio,
                weekend_spend_ratio=features.weekend_spend_ratio,
                food_and_snack_spend_ratio=features.food_and_snack_spend_ratio,
                subscription_spend_ratio=features.subscription_spend_ratio,
                spending_frequency_per_day=features.spending_frequency_per_day,
                spend_trend_ratio=features.spend_trend_ratio,
            ),
        )
