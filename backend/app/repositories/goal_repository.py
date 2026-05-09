from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal


class GoalRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(
        self,
        *,
        user_id: UUID,
        name: str,
        target_amount: Decimal,
        current_amount: Decimal,
        target_date,
        is_completed: bool,
    ) -> Goal:
        goal = Goal(
            user_id=user_id,
            name=name.strip(),
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
            is_completed=is_completed,
        )
        self.db_session.add(goal)
        await self.db_session.flush()
        await self.db_session.refresh(goal)
        return goal

    async def list_by_user(
        self,
        *,
        user_id: UUID,
        is_completed: bool | None = None,
    ) -> list[Goal]:
        query: Select[tuple[Goal]] = select(Goal).where(Goal.user_id == user_id)

        if is_completed is not None:
            query = query.where(Goal.is_completed == is_completed)

        query = query.order_by(Goal.is_completed.asc(), Goal.created_at.desc())

        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_by_id_for_user(
        self,
        *,
        goal_id: UUID,
        user_id: UUID,
    ) -> Goal | None:
        result = await self.db_session.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_progress(
        self,
        *,
        goal: Goal,
        current_amount: Decimal,
        is_completed: bool,
    ) -> Goal:
        goal.current_amount = current_amount
        goal.is_completed = is_completed
        await self.db_session.flush()
        await self.db_session.refresh(goal)
        return goal
