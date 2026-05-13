from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.ml.features import UserSpendingFeatureBuilder
from app.models.expense import Expense


def test_user_spending_feature_builder_creates_behavior_vector() -> None:
    user_id = uuid4()
    expenses = [
        build_expense(user_id, "Coffee", "Morning coffee", "80.00", 1, 9),
        build_expense(user_id, "Coffee", "Morning coffee", "80.00", 2, 9),
        build_expense(user_id, "Coffee", "Morning coffee", "80.00", 3, 9),
        build_expense(user_id, "Transport", "Metro recharge", "300.00", 4, 18),
        build_expense(user_id, "Food Delivery", "Dinner delivery", "700.00", 6, 21),
        build_expense(user_id, "Subscriptions", "Streaming subscription", "500.00", 8, 10),
    ]

    features = UserSpendingFeatureBuilder().build(expenses)

    assert features.transaction_count == 6
    assert features.active_day_count == 6
    assert features.total_spend == Decimal("1740.00")
    assert features.average_transaction_amount == Decimal("290.00")
    assert features.micro_expense_count == 3
    assert features.micro_expense_ratio == Decimal("0.5000")
    assert features.repeated_pattern_count == 1
    assert features.unique_category_count == 4
    assert features.weekend_spend_ratio == Decimal("0.0920")
    assert features.food_and_snack_spend_ratio == Decimal("0.5402")
    assert features.subscription_spend_ratio == Decimal("0.2874")


def test_user_spending_feature_builder_returns_zero_vector_for_empty_history() -> None:
    features = UserSpendingFeatureBuilder().build([])

    assert features.transaction_count == 0
    assert features.total_spend == Decimal("0.00")
    assert features.micro_expense_ratio == Decimal("0.0000")
    assert features.to_model_input()["transaction_count"] == 0


def build_expense(
    user_id,
    category: str,
    description: str,
    amount: str,
    day: int,
    hour: int,
) -> Expense:
    now = datetime(2026, 5, day, hour, tzinfo=UTC)
    return Expense(
        id=uuid4(),
        user_id=user_id,
        amount=Decimal(amount),
        category=category,
        description=description,
        spent_at=now,
        created_at=now,
        updated_at=now,
    )
