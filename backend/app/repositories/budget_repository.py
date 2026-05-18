from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget


class BudgetRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(
        self,
        *,
        user_id: UUID,
        category: str,
        monthly_limit: Decimal,
    ) -> Budget:
        budget = Budget(
            user_id=user_id,
            category=category.strip(),
            monthly_limit=monthly_limit,
        )
        self.db_session.add(budget)
        await self.db_session.flush()
        await self.db_session.refresh(budget)
        return budget

    async def list_by_user(self, *, user_id: UUID) -> list[Budget]:
        query: Select[tuple[Budget]] = (
            select(Budget)
            .where(Budget.user_id == user_id)
            .order_by(Budget.category.asc(), Budget.created_at.desc())
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_by_id_for_user(
        self,
        *,
        budget_id: UUID,
        user_id: UUID,
    ) -> Budget | None:
        result = await self.db_session.execute(
            select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_category_for_user(
        self,
        *,
        category: str,
        user_id: UUID,
    ) -> Budget | None:
        result = await self.db_session.execute(
            select(Budget).where(
                Budget.category == category.strip(),
                Budget.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        *,
        budget: Budget,
        monthly_limit: Decimal,
    ) -> Budget:
        budget.monthly_limit = monthly_limit
        await self.db_session.flush()
        await self.db_session.refresh(budget)
        return budget

    async def delete(self, *, budget: Budget) -> None:
        await self.db_session.delete(budget)
        await self.db_session.flush()
