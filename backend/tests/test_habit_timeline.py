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
from app.schemas.analytics import HabitTimelineEvent, HabitTimelineResponse
from app.services.analytics_service import AnalyticsService


class FakeHabitTimelineRepository:
    async def get_spending_totals(self, **kwargs):
        return Decimal("9000.00"), 18, Decimal("500.00")

    async def get_category_spending_totals(self, **kwargs):
        return [("Food", Decimal("4200.00"), 10), ("Transport", Decimal("4800.00"), 8)]

    async def get_micro_expense_patterns(self, **kwargs):
        return [
            (
                "Food",
                "Tea",
                7,
                Decimal("80.00"),
                Decimal("560.00"),
                datetime(2026, 5, 12, 9, tzinfo=UTC),
            )
        ]

    async def get_weekday_weekend_spending(self, **kwargs):
        return [
            ("weekday", Decimal("4600.00"), 10, Decimal("460.00")),
            ("weekend", Decimal("4400.00"), 8, Decimal("550.00")),
        ]

    async def get_repeated_spending_patterns(self, **kwargs):
        return [
            (
                "Food",
                "Tea",
                7,
                Decimal("1120.00"),
                Decimal("160.00"),
                datetime(2026, 5, 1, 9, tzinfo=UTC),
                datetime(2026, 5, 13, 9, tzinfo=UTC),
            )
        ]

    async def get_spending_trends(self, **kwargs):
        return [
            (datetime(2026, 5, 1, tzinfo=UTC), Decimal("300.00"), 2, Decimal("150.00")),
            (datetime(2026, 5, 13, tzinfo=UTC), Decimal("780.00"), 3, Decimal("260.00")),
        ]


class DummySession:
    pass


@pytest.fixture
def current_user() -> User:
    return User(
        id=uuid4(),
        email="habit-timeline-test@example.com",
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
async def test_build_habit_timeline_returns_behavior_events() -> None:
    service = AnalyticsService(FakeHabitTimelineRepository())

    result = await service.build_habit_timeline(user_id=uuid4())

    event_types = {event.event_type for event in result.events}
    assert "micro_spending" in event_types
    assert "money_leak" in event_types
    assert len(result.events) <= 8
    assert all(event.action for event in result.events)


def test_default_analysis_period_includes_full_current_day() -> None:
    service = AnalyticsService(FakeHabitTimelineRepository())

    _, end_date = service._resolve_analysis_period(start_date=None, end_date=None)

    assert end_date.hour == 23
    assert end_date.minute == 59
    assert end_date.second == 59
    assert end_date.microsecond == 999999


def test_habit_timeline_endpoint_returns_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def build_habit_timeline(self, **kwargs):
        now = datetime(2026, 5, 14, tzinfo=UTC)
        return HabitTimelineResponse(
            start_date=now,
            end_date=now,
            events=[
                HabitTimelineEvent(
                    event_type="micro_spending",
                    severity="warning",
                    title="Tea became a micro-spend pattern",
                    description="Small repeated spends could become a monthly habit cost.",
                    happened_at=now,
                    amount=Decimal("1200.00"),
                    category="Food",
                    action="Set a weekly cap.",
                )
            ],
        )

    monkeypatch.setattr(
        AnalyticsService,
        "build_habit_timeline",
        build_habit_timeline,
    )

    response = client.get("/api/v1/analytics/habit-timeline")

    body = response.json()
    assert response.status_code == 200
    assert body["events"][0]["event_type"] == "micro_spending"
    assert body["events"][0]["title"] == "Tea became a micro-spend pattern"
