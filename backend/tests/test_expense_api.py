from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.main import app
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseListResponse, ExpenseRead
from app.services.expense_service import ExpenseService


class DummySession:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


@pytest.fixture
def current_user() -> User:
    return User(
        id=uuid4(),
        email="api-test@example.com",
        hashed_password="hashed-password",
        is_active=True,
    )


@pytest.fixture
def dummy_session() -> DummySession:
    return DummySession()


@pytest.fixture
def client(
    current_user: User,
    dummy_session: DummySession,
) -> Generator[TestClient, None, None]:
    async def override_current_user() -> User:
        return current_user

    async def override_db_session() -> AsyncGenerator[DummySession, None]:
        yield dummy_session

    app.dependency_overrides[get_current_active_user] = override_current_user
    app.dependency_overrides[get_db_session] = override_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _expense_read(*, expense_id: UUID, user_id: UUID) -> ExpenseRead:
    now = datetime(2026, 5, 8, 12, 0, tzinfo=UTC)
    return ExpenseRead(
        id=expense_id,
        user_id=user_id,
        amount=Decimal("12.50"),
        category="coffee",
        description="latte",
        spent_at=now,
        created_at=now,
        updated_at=now,
    )


def _expense_model(*, expense_id: UUID, user_id: UUID) -> Expense:
    now = datetime(2026, 5, 8, 12, 0, tzinfo=UTC)
    return Expense(
        id=expense_id,
        user_id=user_id,
        amount=Decimal("12.50"),
        category="coffee",
        description="latte",
        spent_at=now,
        created_at=now,
        updated_at=now,
    )


def test_list_expenses_returns_paginated_response(
    client: TestClient,
    current_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expense_id = uuid4()

    async def list_expense_page(self, **kwargs):
        return ExpenseListResponse(
            items=[_expense_read(expense_id=expense_id, user_id=current_user.id)],
            total=1,
            limit=kwargs["limit"],
            offset=kwargs["offset"],
            has_more=False,
        )

    monkeypatch.setattr(ExpenseService, "list_expense_page", list_expense_page)

    response = client.get("/api/v1/expenses?limit=10&offset=0")

    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 1
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert body["has_more"] is False
    assert body["items"][0]["id"] == str(expense_id)


def test_list_expenses_rejects_limit_above_maximum(client: TestClient) -> None:
    response = client.get("/api/v1/expenses?limit=101")

    assert response.status_code == 422


def test_list_expenses_rejects_offset_above_maximum(client: TestClient) -> None:
    response = client.get("/api/v1/expenses?offset=10001")

    assert response.status_code == 422


def test_create_expense_returns_created_expense_and_commits(
    client: TestClient,
    current_user: User,
    dummy_session: DummySession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expense_id = uuid4()

    async def create_expense(self, **kwargs):
        return _expense_model(expense_id=expense_id, user_id=current_user.id)

    monkeypatch.setattr(ExpenseService, "create_expense", create_expense)

    response = client.post(
        "/api/v1/expenses",
        json={
            "amount": "12.50",
            "category": "coffee",
            "description": "latte",
            "spent_at": "2026-05-08T12:00:00Z",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(expense_id)
    assert dummy_session.commit_count == 1


def test_get_expense_returns_expense(
    client: TestClient,
    current_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expense_id = uuid4()

    async def get_expense(self, **kwargs):
        return _expense_read(expense_id=expense_id, user_id=current_user.id)

    monkeypatch.setattr(ExpenseService, "get_expense", get_expense)

    response = client.get(f"/api/v1/expenses/{expense_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(expense_id)


def test_update_expense_returns_updated_expense_and_commits(
    client: TestClient,
    current_user: User,
    dummy_session: DummySession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expense_id = uuid4()

    async def update_expense(self, **kwargs):
        return _expense_read(expense_id=expense_id, user_id=current_user.id)

    monkeypatch.setattr(ExpenseService, "update_expense", update_expense)

    response = client.patch(
        f"/api/v1/expenses/{expense_id}",
        json={"category": "snacks"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "coffee"
    assert dummy_session.commit_count == 1


def test_delete_expense_returns_no_content_and_commits(
    client: TestClient,
    dummy_session: DummySession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def delete_expense(self, **kwargs):
        return None

    monkeypatch.setattr(ExpenseService, "delete_expense", delete_expense)

    response = client.delete(f"/api/v1/expenses/{uuid4()}")

    assert response.status_code == 204
    assert response.content == b""
    assert dummy_session.commit_count == 1
