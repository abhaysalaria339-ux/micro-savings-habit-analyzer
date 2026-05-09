from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Select, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense


class ExpenseRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(
        self,
        *,
        user_id: UUID,
        amount: Decimal,
        category: str,
        description: str | None,
        spent_at: datetime,
    ) -> Expense:
        expense = Expense(
            user_id=user_id,
            amount=amount,
            category=category.strip(),
            description=description.strip() if description else None,
            spent_at=spent_at,
        )
        self.db_session.add(expense)
        await self.db_session.flush()
        await self.db_session.refresh(expense)
        return expense

    async def list_by_user(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Expense]:
        query: Select[tuple[Expense]] = select(Expense).where(Expense.user_id == user_id)

        if start_date is not None:
            query = query.where(Expense.spent_at >= start_date)

        if end_date is not None:
            query = query.where(Expense.spent_at <= end_date)

        if category is not None:
            query = query.where(Expense.category == category.strip())

        query = query.order_by(Expense.spent_at.desc(), Expense.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
    ) -> int:
        query = select(func.count(Expense.id)).where(Expense.user_id == user_id)

        if start_date is not None:
            query = query.where(Expense.spent_at >= start_date)

        if end_date is not None:
            query = query.where(Expense.spent_at <= end_date)

        if category is not None:
            query = query.where(Expense.category == category.strip())

        result = await self.db_session.execute(query)
        return int(result.scalar_one())

    async def get_by_id_for_user(
        self,
        *,
        expense_id: UUID,
        user_id: UUID,
    ) -> Expense | None:
        result = await self.db_session.execute(
            select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        *,
        expense: Expense,
        values: dict[str, Any],
    ) -> Expense:
        if "amount" in values:
            expense.amount = values["amount"]

        if "category" in values:
            expense.category = values["category"].strip()

        if "description" in values:
            description = values["description"]
            expense.description = description.strip() if description else None

        if "spent_at" in values:
            expense.spent_at = values["spent_at"]

        await self.db_session.flush()
        await self.db_session.refresh(expense)
        return expense

    async def delete(self, *, expense: Expense) -> None:
        await self.db_session.delete(expense)
        await self.db_session.flush()

    async def list_for_processing(
        self,
        *,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Expense]:
        query = (
            select(Expense)
            .where(
                Expense.user_id == user_id,
                Expense.spent_at >= start_date,
                Expense.spent_at <= end_date,
            )
            .order_by(Expense.spent_at.asc(), Expense.created_at.asc())
        )

        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_spending_totals(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[Decimal, int, Decimal]:
        query = select(
            func.coalesce(func.sum(Expense.amount), 0),
            func.count(Expense.id),
            func.coalesce(func.avg(Expense.amount), 0),
        ).where(Expense.user_id == user_id)

        query = self._apply_date_filters(query, start_date=start_date, end_date=end_date)

        total_amount, transaction_count, average_amount = (
            await self.db_session.execute(query)
        ).one()

        return Decimal(total_amount), int(transaction_count), Decimal(average_amount)

    async def get_category_spending_totals(
        self,
        *,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[tuple[str, Decimal, int]]:
        query = (
            select(
                Expense.category,
                func.coalesce(func.sum(Expense.amount), 0),
                func.count(Expense.id),
            )
            .where(Expense.user_id == user_id)
            .group_by(Expense.category)
            .order_by(desc(func.sum(Expense.amount)))
        )

        query = self._apply_date_filters(query, start_date=start_date, end_date=end_date)

        result = await self.db_session.execute(query)
        return [
            (category, Decimal(total_amount), int(transaction_count))
            for category, total_amount, transaction_count in result.all()
        ]

    async def get_micro_expense_patterns(
        self,
        *,
        user_id: UUID,
        max_expense_amount: Decimal,
        min_occurrences: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[tuple[str, str | None, int, Decimal, Decimal, datetime]]:
        query = (
            select(
                Expense.category,
                Expense.description,
                func.count(Expense.id),
                func.coalesce(func.avg(Expense.amount), 0),
                func.coalesce(func.sum(Expense.amount), 0),
                func.max(Expense.spent_at),
            )
            .where(
                Expense.user_id == user_id,
                Expense.amount <= max_expense_amount,
                Expense.spent_at >= start_date,
                Expense.spent_at <= end_date,
            )
            .group_by(Expense.category, Expense.description)
            .having(func.count(Expense.id) >= min_occurrences)
            .order_by(desc(func.sum(Expense.amount)))
        )

        result = await self.db_session.execute(query)
        return [
            (
                category,
                description,
                int(occurrence_count),
                Decimal(average_amount),
                Decimal(total_amount),
                latest_spent_at,
            )
            for (
                category,
                description,
                occurrence_count,
                average_amount,
                total_amount,
                latest_spent_at,
            ) in result.all()
        ]

    async def get_weekday_weekend_spending(
        self,
        *,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> list[tuple[str, Decimal, int, Decimal]]:
        period_type = case(
            (func.extract("isodow", Expense.spent_at).in_([6, 7]), "weekend"),
            else_="weekday",
        ).label("period_type")

        query = (
            select(
                period_type,
                func.coalesce(func.sum(Expense.amount), 0),
                func.count(Expense.id),
                func.coalesce(func.avg(Expense.amount), 0),
            )
            .where(
                Expense.user_id == user_id,
                Expense.spent_at >= start_date,
                Expense.spent_at <= end_date,
            )
            .group_by(period_type)
        )

        result = await self.db_session.execute(query)
        return [
            (
                period,
                Decimal(total_amount),
                int(transaction_count),
                Decimal(average_amount),
            )
            for period, total_amount, transaction_count, average_amount in result.all()
        ]

    async def get_repeated_spending_patterns(
        self,
        *,
        user_id: UUID,
        min_occurrences: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[tuple[str, str | None, int, Decimal, Decimal, datetime, datetime]]:
        query = (
            select(
                Expense.category,
                Expense.description,
                func.count(Expense.id),
                func.coalesce(func.sum(Expense.amount), 0),
                func.coalesce(func.avg(Expense.amount), 0),
                func.min(Expense.spent_at),
                func.max(Expense.spent_at),
            )
            .where(
                Expense.user_id == user_id,
                Expense.spent_at >= start_date,
                Expense.spent_at <= end_date,
            )
            .group_by(Expense.category, Expense.description)
            .having(func.count(Expense.id) >= min_occurrences)
            .order_by(desc(func.sum(Expense.amount)))
        )

        result = await self.db_session.execute(query)
        return [
            (
                category,
                description,
                int(occurrence_count),
                Decimal(total_amount),
                Decimal(average_amount),
                first_spent_at,
                latest_spent_at,
            )
            for (
                category,
                description,
                occurrence_count,
                total_amount,
                average_amount,
                first_spent_at,
                latest_spent_at,
            ) in result.all()
        ]

    async def get_spending_trends(
        self,
        *,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
        interval: str,
    ) -> list[tuple[datetime, Decimal, int, Decimal]]:
        period_start = func.date_trunc(interval, Expense.spent_at).label("period_start")
        query = (
            select(
                period_start,
                func.coalesce(func.sum(Expense.amount), 0),
                func.count(Expense.id),
                func.coalesce(func.avg(Expense.amount), 0),
            )
            .where(
                Expense.user_id == user_id,
                Expense.spent_at >= start_date,
                Expense.spent_at <= end_date,
            )
            .group_by(period_start)
            .order_by(period_start.asc())
        )

        result = await self.db_session.execute(query)
        return [
            (
                period_start_value,
                Decimal(total_amount),
                int(transaction_count),
                Decimal(average_amount),
            )
            for period_start_value, total_amount, transaction_count, average_amount in result.all()
        ]

    def _apply_date_filters(
        self,
        query,
        *,
        start_date: datetime | None,
        end_date: datetime | None,
    ):
        if start_date is not None:
            query = query.where(Expense.spent_at >= start_date)

        if end_date is not None:
            query = query.where(Expense.spent_at <= end_date)

        return query
