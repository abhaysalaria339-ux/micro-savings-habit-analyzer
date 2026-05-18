from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.main import app
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetRead
from app.services.budget_service import BudgetService


@dataclass
class FakeBudget:
    id: UUID
    user_id: UUID
    category: str
    monthly_limit: Decimal
    created_at: datetime
    updated_at: datetime


class FakeBudgetRepository:
    def __init__(self) -> None:
        self.budget: FakeBudget | None = None

    async def get_by_category_for_user(self, *, category: str, user_id: UUID):
        if self.budget and self.budget.category == category and self.budget.user_id == user_id:
            return self.budget
        return None

    async def create(self, *, user_id: UUID, category: str, monthly_limit: Decimal):
        now = datetime.now(UTC)
        self.budget = FakeBudget(
            id=uuid4(),
            user_id=user_id,
            category=category,
            monthly_limit=monthly_limit,
            created_at=now,
            updated_at=now,
        )
        return self.budget

    async def list_by_user(self, *, user_id: UUID):
        if self.budget and self.budget.user_id == user_id:
            return [self.budget]
        return []

    async def get_by_id_for_user(self, *, budget_id: UUID, user_id: UUID):
        if self.budget and self.budget.id == budget_id and self.budget.user_id == user_id:
            return self.budget
        return None

    async def update(self, *, budget: FakeBudget, monthly_limit: Decimal):
        budget.monthly_limit = monthly_limit
        budget.updated_at = datetime.now(UTC)
        return budget


class FakeBudgetExpenseRepository:
    async def get_category_spending_totals(self, **kwargs):
        return [("Food", Decimal("850.00"), 4)]


class DummySession:
    pass


@pytest.fixture
def current_user() -> User:
    return User(
        id=uuid4(),
        email="budget-test@example.com",
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
async def test_budget_service_returns_usage_status() -> None:
    user_id = uuid4()
    service = BudgetService(FakeBudgetRepository(), FakeBudgetExpenseRepository())

    result = await service.upsert_budget(
        user_id=user_id,
        budget_create=BudgetCreate(category="Food", monthly_limit=Decimal("1000.00")),
    )

    assert result.category == "Food"
    assert result.spent_amount == Decimal("850.00")
    assert result.remaining_amount == Decimal("150.00")
    assert result.status == "watch"


def test_budget_endpoint_returns_budget_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def list_budgets(self, **kwargs):
        _ = self, kwargs
        now = datetime(2026, 5, 18, tzinfo=UTC)
        return [
            BudgetRead(
                id=uuid4(),
                user_id=uuid4(),
                category="Food",
                monthly_limit=Decimal("1000.00"),
                spent_amount=Decimal("850.00"),
                remaining_amount=Decimal("150.00"),
                usage_percentage=Decimal("85.00"),
                status="watch",
                period_start=now,
                period_end=now,
                created_at=now,
                updated_at=now,
            )
        ]

    monkeypatch.setattr(BudgetService, "list_budgets", list_budgets)

    response = client.get("/api/v1/budgets")

    assert response.status_code == 200
    assert response.json()[0]["category"] == "Food"
