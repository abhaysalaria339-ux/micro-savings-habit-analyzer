from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.models.goal import Goal
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import GoalCreate, GoalProgressUpdate, GoalRead


class GoalNotFoundError(Exception):
    pass


class GoalService:
    def __init__(self, goal_repository: GoalRepository) -> None:
        self.goal_repository = goal_repository

    async def create_goal(
        self,
        *,
        user_id: UUID,
        goal_create: GoalCreate,
    ) -> GoalRead:
        goal = await self.goal_repository.create(
            user_id=user_id,
            name=goal_create.name,
            target_amount=goal_create.target_amount,
            current_amount=goal_create.current_amount,
            target_date=goal_create.target_date,
            is_completed=goal_create.current_amount >= goal_create.target_amount,
        )
        return self.to_goal_read(goal)

    async def list_goals(
        self,
        *,
        user_id: UUID,
        is_completed: bool | None = None,
    ) -> list[GoalRead]:
        goals = await self.goal_repository.list_by_user(
            user_id=user_id,
            is_completed=is_completed,
        )
        return [self.to_goal_read(goal) for goal in goals]

    async def update_goal_progress(
        self,
        *,
        goal_id: UUID,
        user_id: UUID,
        progress_update: GoalProgressUpdate,
    ) -> GoalRead:
        goal = await self.goal_repository.get_by_id_for_user(
            goal_id=goal_id,
            user_id=user_id,
        )
        if goal is None:
            raise GoalNotFoundError("Goal not found.")

        updated_goal = await self.goal_repository.update_progress(
            goal=goal,
            current_amount=progress_update.current_amount,
            is_completed=progress_update.current_amount >= goal.target_amount,
        )
        return self.to_goal_read(updated_goal)

    def to_goal_read(self, goal: Goal) -> GoalRead:
        return GoalRead(
            id=goal.id,
            user_id=goal.user_id,
            name=goal.name,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            progress_percentage=self._calculate_progress_percentage(
                current_amount=goal.current_amount,
                target_amount=goal.target_amount,
            ),
            target_date=goal.target_date,
            is_completed=goal.is_completed,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )

    def _calculate_progress_percentage(
        self,
        *,
        current_amount: Decimal,
        target_amount: Decimal,
    ) -> Decimal:
        if target_amount <= Decimal("0"):
            return Decimal("0.00")

        progress = (current_amount / target_amount) * Decimal("100")
        capped_progress = min(progress, Decimal("100"))
        return capped_progress.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
