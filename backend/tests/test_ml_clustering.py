from decimal import Decimal

from app.ml.clustering import SpendingProfileClusteringModel
from app.ml.features import UserSpendingFeatureVector


def test_spending_profile_clustering_detects_micro_spender() -> None:
    features = build_feature_vector(
        transaction_count=95,
        micro_expense_ratio=Decimal("0.7200"),
        weekend_spend_ratio=Decimal("0.2300"),
        food_and_snack_spend_ratio=Decimal("0.5900"),
        spending_frequency_per_day=Decimal("2.5000"),
        average_transaction_amount=Decimal("220.00"),
    )

    prediction = SpendingProfileClusteringModel().predict(features)

    assert prediction.cluster_id == "micro_spender"
    assert prediction.profile_label == "Micro-Spender"
    assert prediction.confidence > Decimal("0.6000")
    assert prediction.reasons
    assert prediction.recommendations


def test_spending_profile_clustering_requires_enough_data() -> None:
    features = build_feature_vector(transaction_count=3)

    prediction = SpendingProfileClusteringModel().predict(features)

    assert prediction.cluster_id == "insufficient_data"
    assert prediction.confidence == Decimal("0.0000")


def build_feature_vector(
    *,
    transaction_count: int,
    micro_expense_ratio: Decimal = Decimal("0.2500"),
    weekend_spend_ratio: Decimal = Decimal("0.2500"),
    food_and_snack_spend_ratio: Decimal = Decimal("0.2500"),
    spending_frequency_per_day: Decimal = Decimal("0.4000"),
    average_transaction_amount: Decimal = Decimal("500.00"),
) -> UserSpendingFeatureVector:
    return UserSpendingFeatureVector(
        transaction_count=transaction_count,
        active_day_count=30,
        total_spend=Decimal("15000.00"),
        average_transaction_amount=average_transaction_amount,
        average_daily_spend=Decimal("500.00"),
        micro_expense_count=20,
        micro_expense_ratio=micro_expense_ratio,
        repeated_pattern_count=4,
        unique_category_count=5,
        top_category_spend_ratio=Decimal("0.3800"),
        weekend_spend_ratio=weekend_spend_ratio,
        food_and_snack_spend_ratio=food_and_snack_spend_ratio,
        subscription_spend_ratio=Decimal("0.0500"),
        spending_frequency_per_day=spending_frequency_per_day,
        first_half_spend=Decimal("7000.00"),
        second_half_spend=Decimal("8000.00"),
        spend_trend_ratio=Decimal("0.1429"),
    )
