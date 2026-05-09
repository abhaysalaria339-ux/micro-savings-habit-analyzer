from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.expense import Expense
from app.schemas.expense import ExpenseUpdate
from app.services.expense_service import ExpenseNotFoundError, ExpenseService


class FakeExpenseRepository:
    def __init__(self, *, total: int) -> None:
        self.total = total
        self.list_args = None
        self.count_args = None
        self.updated_values = None
        self.deleted_expense = None

    async def list_by_user(self, **kwargs):
        self.list_args = kwargs
        now = datetime(2026, 5, 8, tzinfo=UTC)
        return [
            Expense(
                id=uuid4(),
                user_id=kwargs["user_id"],
                amount=Decimal("5.50"),
                category="coffee",
                description="latte",
                spent_at=now,
                created_at=now,
                updated_at=now,
            )
        ]

    async def count_by_user(self, **kwargs):
        self.count_args = kwargs
        return self.total

    async def get_by_id_for_user(self, **kwargs):
        now = datetime(2026, 5, 8, tzinfo=UTC)
        return Expense(
            id=kwargs["expense_id"],
            user_id=kwargs["user_id"],
            amount=Decimal("5.50"),
            category="coffee",
            description="latte",
            spent_at=now,
            created_at=now,
            updated_at=now,
        )

    async def update(self, *, expense, values):
        self.updated_values = values
        for field, value in values.items():
            setattr(expense, field, value)
        return expense

    async def delete(self, *, expense):
        self.deleted_expense = expense


@pytest.mark.asyncio
async def test_list_expense_page_returns_pagination_metadata() -> None:
    user_id = uuid4()
    repository = FakeExpenseRepository(total=3)
    service = ExpenseService(repository)

    response = await service.list_expense_page(
        user_id=user_id,
        category="coffee",
        limit=1,
        offset=1,
    )

    assert response.total == 3
    assert response.limit == 1
    assert response.offset == 1
    assert response.has_more is True
    assert len(response.items) == 1
    assert repository.list_args["category"] == "coffee"
    assert repository.count_args["category"] == "coffee"


@pytest.mark.asyncio
async def test_list_expense_page_rejects_invalid_limit() -> None:
    service = ExpenseService(FakeExpenseRepository(total=0))

    with pytest.raises(ValueError, match="Pagination limit"):
        await service.list_expense_page(
            user_id=uuid4(),
            limit=101,
            offset=0,
        )


@pytest.mark.asyncio
async def test_list_expense_page_rejects_invalid_offset() -> None:
    service = ExpenseService(FakeExpenseRepository(total=0))

    with pytest.raises(ValueError, match="Pagination offset"):
        await service.list_expense_page(
            user_id=uuid4(),
            limit=10,
            offset=10_001,
        )


@pytest.mark.asyncio
async def test_get_expense_returns_owned_expense() -> None:
    user_id = uuid4()
    expense_id = uuid4()
    service = ExpenseService(FakeExpenseRepository(total=1))

    response = await service.get_expense(expense_id=expense_id, user_id=user_id)

    assert response.id == expense_id
    assert response.user_id == user_id
    assert response.category == "coffee"


@pytest.mark.asyncio
async def test_get_expense_raises_when_expense_is_missing() -> None:
    class MissingExpenseRepository(FakeExpenseRepository):
        async def get_by_id_for_user(self, **kwargs):
            return None

    service = ExpenseService(MissingExpenseRepository(total=0))

    with pytest.raises(ExpenseNotFoundError):
        await service.get_expense(expense_id=uuid4(), user_id=uuid4())


@pytest.mark.asyncio
async def test_update_expense_updates_only_provided_fields() -> None:
    user_id = uuid4()
    expense_id = uuid4()
    repository = FakeExpenseRepository(total=1)
    service = ExpenseService(repository)

    response = await service.update_expense(
        expense_id=expense_id,
        user_id=user_id,
        expense_update=ExpenseUpdate(category="snacks"),
    )

    assert response.id == expense_id
    assert response.category == "snacks"
    assert repository.updated_values == {"category": "snacks"}


@pytest.mark.asyncio
async def test_update_expense_raises_when_expense_is_missing() -> None:
    class MissingExpenseRepository(FakeExpenseRepository):
        async def get_by_id_for_user(self, **kwargs):
            return None

    service = ExpenseService(MissingExpenseRepository(total=0))

    with pytest.raises(ExpenseNotFoundError):
        await service.update_expense(
            expense_id=uuid4(),
            user_id=uuid4(),
            expense_update=ExpenseUpdate(category="snacks"),
        )


@pytest.mark.asyncio
async def test_delete_expense_deletes_owned_expense() -> None:
    user_id = uuid4()
    expense_id = uuid4()
    repository = FakeExpenseRepository(total=1)
    service = ExpenseService(repository)

    await service.delete_expense(expense_id=expense_id, user_id=user_id)

    assert repository.deleted_expense is not None
    assert repository.deleted_expense.id == expense_id
    assert repository.deleted_expense.user_id == user_id


@pytest.mark.asyncio
async def test_delete_expense_raises_when_expense_is_missing() -> None:
    class MissingExpenseRepository(FakeExpenseRepository):
        async def get_by_id_for_user(self, **kwargs):
            return None

    service = ExpenseService(MissingExpenseRepository(total=0))

    with pytest.raises(ExpenseNotFoundError):
        await service.delete_expense(expense_id=uuid4(), user_id=uuid4())
