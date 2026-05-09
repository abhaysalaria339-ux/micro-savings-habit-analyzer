from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ProcessedExpense(BaseModel):
    amount: Decimal
    category: str
    description: str | None
    spent_at: datetime


class PipelineCategoryAggregate(BaseModel):
    category: str
    total_amount: Decimal
    transaction_count: int


class PipelineFeatureSet(BaseModel):
    transaction_count: int
    total_amount: Decimal
    average_expense_amount: Decimal
    unique_category_count: int
    micro_expense_count: int
    repeated_pattern_count: int


class DataPipelineResult(BaseModel):
    start_date: datetime
    end_date: datetime
    cleaned_record_count: int
    features: PipelineFeatureSet
    category_aggregates: list[PipelineCategoryAggregate]
    generated_insights: list[str]
