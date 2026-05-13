from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

MLProblemType = Literal["clustering", "classification", "forecasting"]


class MLCapability(BaseModel):
    problem_type: MLProblemType
    status: Literal["planned", "available"]
    description: str
    required_feature_groups: list[str]


class MLReadinessResponse(BaseModel):
    ml_enabled: bool
    model_execution_available: bool
    capabilities: list[MLCapability]


class MLFeatureSnapshot(BaseModel):
    total_spend: Decimal
    average_transaction_amount: Decimal
    average_daily_spend: Decimal
    micro_expense_ratio: Decimal
    repeated_pattern_count: int
    unique_category_count: int
    top_category_spend_ratio: Decimal
    weekend_spend_ratio: Decimal
    food_and_snack_spend_ratio: Decimal
    subscription_spend_ratio: Decimal
    spending_frequency_per_day: Decimal
    spend_trend_ratio: Decimal


class MLSpendingProfileResponse(BaseModel):
    profile_id: str
    profile_label: str
    confidence: Decimal
    summary: str
    reasons: list[str]
    recommendations: list[str]
    analysis_days: int
    transaction_count: int
    features: MLFeatureSnapshot
