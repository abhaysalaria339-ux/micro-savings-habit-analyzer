from collections.abc import AsyncGenerator, Generator
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.main import app
from app.models.user import User
from app.schemas.ml import MLFeatureSnapshot, MLSpendingProfileResponse
from app.services.ml_spending_profile_service import MLSpendingProfileService


class DummySession:
    pass


@pytest.fixture
def current_user() -> User:
    return User(
        id=uuid4(),
        email="ml-api-test@example.com",
        hashed_password="hashed-password",
        is_active=True,
    )


@pytest.fixture
def client(current_user: User) -> Generator[TestClient, None, None]:
    async def override_current_user() -> User:
        return current_user

    async def override_db_session() -> AsyncGenerator[DummySession, None]:
        yield DummySession()

    app.dependency_overrides[get_current_active_user] = override_current_user
    app.dependency_overrides[get_db_session] = override_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_ml_spending_profile_returns_cluster_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def get_spending_profile(self, **kwargs):
        return MLSpendingProfileResponse(
            profile_id="micro_spender",
            profile_label="Micro-Spender",
            confidence=Decimal("0.8123"),
            summary="Many small purchases appear repeatedly.",
            reasons=["A high share of transactions are micro-expenses."],
            recommendations=["Pause one repeated micro-expense for seven days."],
            analysis_days=kwargs["analysis_days"],
            transaction_count=42,
            features=MLFeatureSnapshot(
                total_spend=Decimal("12000.00"),
                average_transaction_amount=Decimal("285.71"),
                average_daily_spend=Decimal("400.00"),
                micro_expense_ratio=Decimal("0.6500"),
                repeated_pattern_count=5,
                unique_category_count=6,
                top_category_spend_ratio=Decimal("0.4200"),
                weekend_spend_ratio=Decimal("0.2400"),
                food_and_snack_spend_ratio=Decimal("0.5500"),
                subscription_spend_ratio=Decimal("0.0500"),
                spending_frequency_per_day=Decimal("1.4000"),
                spend_trend_ratio=Decimal("0.1000"),
            ),
        )

    monkeypatch.setattr(
        MLSpendingProfileService,
        "get_spending_profile",
        get_spending_profile,
    )

    response = client.get("/api/v1/ml/spending-profile?analysis_days=30")

    body = response.json()
    assert response.status_code == 200
    assert body["profile_id"] == "micro_spender"
    assert body["profile_label"] == "Micro-Spender"
    assert body["analysis_days"] == 30
    assert body["transaction_count"] == 42


def test_get_ml_spending_profile_rejects_short_analysis_window(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/ml/spending-profile?analysis_days=7")

    assert response.status_code == 422
