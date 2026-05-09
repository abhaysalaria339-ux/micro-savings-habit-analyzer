from datetime import datetime
from uuid import UUID

from app.core.pagination import DEFAULT_PAGE_LIMIT, validate_pagination
from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate, ExpenseListResponse, ExpenseRead, ExpenseUpdate


class ExpenseNotFoundError(Exception):
    pass


class ExpenseService:
    def __init__(self, expense_repository: ExpenseRepository) -> None:
        self.expense_repository = expense_repository

    async def create_expense(
        self,
        *,
        user_id: UUID,
        expense_create: ExpenseCreate,
    ) -> Expense:
        return await self.expense_repository.create(
            user_id=user_id,
            amount=expense_create.amount,
            category=expense_create.category,
            description=expense_create.description,
            spent_at=expense_create.spent_at,
        )

    async def list_expenses(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> list[Expense]:
        validate_pagination(limit=limit, offset=offset)

        return await self.expense_repository.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit,
            offset=offset,
        )

    async def list_expense_page(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> ExpenseListResponse:
        validate_pagination(limit=limit, offset=offset)

        expenses = await self.list_expenses(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit,
            offset=offset,
        )
        total = await self.expense_repository.count_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
        )

        items = [ExpenseRead.model_validate(expense) for expense in expenses]
        return ExpenseListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=offset + len(items) < total,
        )

    async def get_expense(
        self,
        *,
        expense_id: UUID,
        user_id: UUID,
    ) -> ExpenseRead:
        expense = await self.expense_repository.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )
        if expense is None:
            raise ExpenseNotFoundError("Expense not found.")

        return ExpenseRead.model_validate(expense)

    async def update_expense(
        self,
        *,
        expense_id: UUID,
        user_id: UUID,
        expense_update: ExpenseUpdate,
    ) -> ExpenseRead:
        expense = await self.expense_repository.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )
        if expense is None:
            raise ExpenseNotFoundError("Expense not found.")

        updated_expense = await self.expense_repository.update(
            expense=expense,
            values=expense_update.model_dump(exclude_unset=True),
        )
        return ExpenseRead.model_validate(updated_expense)

    async def delete_expense(
        self,
        *,
        expense_id: UUID,
        user_id: UUID,
    ) -> None:
        expense = await self.expense_repository.get_by_id_for_user(
            expense_id=expense_id,
            user_id=user_id,
        )
        if expense is None:
            raise ExpenseNotFoundError("Expense not found.")

        await self.expense_repository.delete(expense=expense)
