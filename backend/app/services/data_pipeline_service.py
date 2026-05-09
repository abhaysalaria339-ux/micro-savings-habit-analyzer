from datetime import UTC, datetime
from uuid import UUID

from app.pipelines.expense_aggregation import ExpenseAggregationPipeline
from app.pipelines.expense_cleaning import ExpenseCleaningPipeline
from app.pipelines.feature_engineering import ExpenseFeatureEngineeringPipeline
from app.pipelines.insight_generation import PipelineInsightGeneration
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.pipeline import DataPipelineResult


class DataPipelineService:
    def __init__(self, expense_repository: ExpenseRepository) -> None:
        self.expense_repository = expense_repository
        self.cleaning_pipeline = ExpenseCleaningPipeline()
        self.aggregation_pipeline = ExpenseAggregationPipeline()
        self.feature_pipeline = ExpenseFeatureEngineeringPipeline()
        self.insight_pipeline = PipelineInsightGeneration()

    async def run_expense_pipeline(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> DataPipelineResult:
        resolved_start_date, resolved_end_date = self._resolve_period(
            start_date=start_date,
            end_date=end_date,
        )
        expenses = await self.expense_repository.list_for_processing(
            user_id=user_id,
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )
        cleaned_expenses = self.cleaning_pipeline.clean(expenses)
        category_aggregates = self.aggregation_pipeline.aggregate_by_category(cleaned_expenses)
        features = self.feature_pipeline.build_features(cleaned_expenses)
        generated_insights = self.insight_pipeline.generate(
            features=features,
            category_aggregates=category_aggregates,
        )

        return DataPipelineResult(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
            cleaned_record_count=len(cleaned_expenses),
            features=features,
            category_aggregates=category_aggregates,
            generated_insights=generated_insights,
        )

    def _resolve_period(
        self,
        *,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        resolved_start_date = start_date or now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        resolved_end_date = end_date or now
        return (
            self._normalize_datetime(resolved_start_date),
            self._normalize_datetime(resolved_end_date),
        )

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=UTC)

        return value
