from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.models.budget import Budget
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate


class BudgetNotFoundError(Exception):
    pass


class BudgetService:
    def __init__(
        self,
        budget_repository: BudgetRepository,
        expense_repository: ExpenseRepository,
    ) -> None:
        self.budget_repository = budget_repository
        self.expense_repository = expense_repository

    async def upsert_budget(
        self,
        *,
        user_id: UUID,
        budget_create: BudgetCreate,
    ) -> BudgetRead:
        existing_budget = await self.budget_repository.get_by_category_for_user(
            category=budget_create.category,
            user_id=user_id,
        )
        if existing_budget is None:
            budget = await self.budget_repository.create(
                user_id=user_id,
                category=budget_create.category,
                monthly_limit=budget_create.monthly_limit,
            )
        else:
            budget = await self.budget_repository.update(
                budget=existing_budget,
                monthly_limit=budget_create.monthly_limit,
            )

        return await self.to_budget_read(budget)

    async def list_budgets(self, *, user_id: UUID) -> list[BudgetRead]:
        budgets = await self.budget_repository.list_by_user(user_id=user_id)
        return [await self.to_budget_read(budget) for budget in budgets]

    async def update_budget(
        self,
        *,
        budget_id: UUID,
        user_id: UUID,
        budget_update: BudgetUpdate,
    ) -> BudgetRead:
        budget = await self.budget_repository.get_by_id_for_user(
            budget_id=budget_id,
            user_id=user_id,
        )
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")

        updated_budget = await self.budget_repository.update(
            budget=budget,
            monthly_limit=budget_update.monthly_limit,
        )
        return await self.to_budget_read(updated_budget)

    async def delete_budget(self, *, budget_id: UUID, user_id: UUID) -> None:
        budget = await self.budget_repository.get_by_id_for_user(
            budget_id=budget_id,
            user_id=user_id,
        )
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")

        await self.budget_repository.delete(budget=budget)

    async def to_budget_read(self, budget: Budget) -> BudgetRead:
        period_start, period_end = self._current_month_range()
        spent_amount = await self._get_category_spend(
            user_id=budget.user_id,
            category=budget.category,
            start_date=period_start,
            end_date=period_end,
        )
        remaining_amount = max(budget.monthly_limit - spent_amount, Decimal("0.00"))
        usage_percentage = self._percentage(
            spent_amount=spent_amount,
            monthly_limit=budget.monthly_limit,
        )

        return BudgetRead(
            id=budget.id,
            user_id=budget.user_id,
            category=budget.category,
            monthly_limit=self._money(budget.monthly_limit),
            spent_amount=self._money(spent_amount),
            remaining_amount=self._money(remaining_amount),
            usage_percentage=usage_percentage,
            status=self._status(usage_percentage=usage_percentage),
            period_start=period_start,
            period_end=period_end,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
        )

    async def _get_category_spend(
        self,
        *,
        user_id: UUID,
        category: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Decimal:
        totals = await self.expense_repository.get_category_spending_totals(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        for current_category, total_amount, _transaction_count in totals:
            if current_category == category:
                return total_amount

        return Decimal("0.00")

    def _current_month_range(self) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return period_start, now

    def _percentage(self, *, spent_amount: Decimal, monthly_limit: Decimal) -> Decimal:
        if monthly_limit <= Decimal("0.00"):
            return Decimal("0.00")

        return self._money((spent_amount / monthly_limit) * Decimal("100"))

    def _status(self, *, usage_percentage: Decimal) -> str:
        if usage_percentage >= Decimal("100.00"):
            return "over"

        if usage_percentage >= Decimal("80.00"):
            return "watch"

        return "safe"

    def _money(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
