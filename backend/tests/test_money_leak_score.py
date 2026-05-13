from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.main import app
from app.models.user import User
from app.schemas.analytics import MoneyLeakScore, MoneyLeakScoreEvidence
from app.services.analytics_service import AnalyticsService


class FakeMoneyLeakRepository:
    async def get_spending_totals(self, **kwargs):
        return Decimal("12000.00"), 24, Decimal("500.00")

    async def get_category_spending_totals(self, **kwargs):
        return [("Coffee", Decimal("3200.00"), 16), ("Transport", Decimal("8800.00"), 8)]

    async def get_repeated_spending_patterns(self, **kwargs):
        first = datetime(2026, 5, 1, 9, tzinfo=UTC)
        latest = datetime(2026, 5, 22, 9, tzinfo=UTC)
        return [
            (
                "Coffee",
                "Morning coffee",
                8,
                Decimal("2400.00"),
                Decimal("300.00"),
                first,
                latest,
            ),
            (
                "Snacks",
                "Evening snack",
                5,
                Decimal("900.00"),
                Decimal("180.00"),
                first,
                latest,
            ),
        ]


class DummySession:
    pass


@pytest.fixture
def current_user() -> User:
    return User(
        id=uuid4(),
        email="money-leak-test@example.com",
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


@pytest.mark.asyncio
async def test_calculate_money_leak_score_returns_explainable_score() -> None:
    service = AnalyticsService(FakeMoneyLeakRepository())

    result = await service.calculate_money_leak_score(user_id=uuid4())

    assert result.score >= 60
    assert result.risk_level in {"high", "critical"}
    assert result.projected_monthly_leak > Decimal("0.00")
    assert result.pattern_count == 2
    assert result.top_leak_category == "Coffee"
    assert result.recommended_action
    assert len(result.evidence) >= 3


def test_money_leak_score_endpoint_returns_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def calculate_money_leak_score(self, **kwargs):
        now = datetime(2026, 5, 14, tzinfo=UTC)
        return MoneyLeakScore(
            start_date=now,
            end_date=now,
            score=72,
            risk_level="high",
            projected_monthly_leak=Decimal("3300.00"),
            leak_ratio=Decimal("27.50"),
            pattern_count=2,
            top_leak_category="Coffee",
            summary="Morning coffee is the strongest leak signal.",
            recommended_action="Pause Morning coffee for seven days.",
            evidence=[
                MoneyLeakScoreEvidence(
                    name="projected_leak_ratio",
                    impact=35,
                    message="Projected monthly leaks equal 27.50% of selected-period spending.",
                )
            ],
        )

    monkeypatch.setattr(
        AnalyticsService,
        "calculate_money_leak_score",
        calculate_money_leak_score,
    )

    response = client.get("/api/v1/analytics/money-leak-score")

    body = response.json()
    assert response.status_code == 200
    assert body["score"] == 72
    assert body["risk_level"] == "high"
    assert body["top_leak_category"] == "Coffee"
