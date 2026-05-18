from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.main import app
from app.models.user import User
from app.schemas.advanced import (
    AdvancedIntelligenceResponse,
    CalendarHeatmapResponse,
    RecurringExpenseResponse,
    WeeklyFinancialHealthReport,
)
from app.services.advanced_intelligence_service import AdvancedIntelligenceService


@dataclass
class FakeExpense:
    amount: Decimal
    category: str
    description: str | None
    spent_at: datetime


class FakeAdvancedExpenseRepository:
    def __init__(self, expenses: list[FakeExpense]) -> None:
        self.expenses = expenses

    async def list_for_processing(
        self,
        *,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> list[FakeExpense]:
        _ = user_id
        return [
            expense
            for expense in self.expenses
            if start_date <= expense.spent_at <= end_date
        ]


class DummySession:
    pass


@pytest.fixture
def current_user() -> User:
    return User(
        id=uuid4(),
        email="advanced-test@example.com",
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
async def test_advanced_intelligence_builds_behavior_signals() -> None:
    now = datetime.now(UTC)
    expenses = [
        FakeExpense(
            amount=Decimal("60.00"),
            category="Snacks",
            description="Small snack purchase",
            spent_at=now - timedelta(days=day),
        )
        for day in (1, 3, 5, 7, 9)
    ]
    expenses.extend(
        [
            FakeExpense(
                amount=Decimal("3500.00"),
                category="Shopping",
                description="Headphones",
                spent_at=now - timedelta(days=2),
            ),
            FakeExpense(
                amount=Decimal("420.00"),
                category="Transport",
                description="Cab",
                spent_at=now - timedelta(days=11),
            ),
        ]
    )

    service = AdvancedIntelligenceService(FakeAdvancedExpenseRepository(expenses))

    result = await service.get_advanced_intelligence(user_id=uuid4(), analysis_days=30)

    assert result.analysis_days == 30
    assert result.recurring_expenses.candidates
    assert result.recurring_expenses.candidates[0].category == "Snacks"
    assert result.calendar_heatmap.days
    assert result.weekly_report.total_spend > Decimal("0.00")
    assert result.anomalies
    assert result.coach_recommendations


def test_advanced_intelligence_endpoint_returns_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def get_advanced_intelligence(self, **kwargs):
        _ = self, kwargs
        now = datetime(2026, 5, 18, tzinfo=UTC)
        return AdvancedIntelligenceResponse(
            analysis_days=30,
            recurring_expenses=RecurringExpenseResponse(
                start_date=now - timedelta(days=29),
                end_date=now,
                candidates=[],
            ),
            calendar_heatmap=CalendarHeatmapResponse(
                start_date=now - timedelta(days=29),
                end_date=now,
                max_daily_amount=Decimal("0.00"),
                days=[],
            ),
            weekly_report=WeeklyFinancialHealthReport(
                start_date=now - timedelta(days=6),
                end_date=now,
                total_spend=Decimal("0.00"),
                previous_total_spend=Decimal("0.00"),
                spend_change_percentage=Decimal("0.00"),
                top_category=None,
                top_category_amount=Decimal("0.00"),
                recurring_monthly_risk=Decimal("0.00"),
                high_spend_days=0,
                summary="No expenses were found for the current week.",
                recommended_focus="Keep tracking daily expenses.",
            ),
            anomalies=[],
            coach_recommendations=[],
        )

    monkeypatch.setattr(
        AdvancedIntelligenceService,
        "get_advanced_intelligence",
        get_advanced_intelligence,
    )

    response = client.get("/api/v1/advanced/intelligence?analysis_days=30")

    assert response.status_code == 200
    assert response.json()["analysis_days"] == 30
