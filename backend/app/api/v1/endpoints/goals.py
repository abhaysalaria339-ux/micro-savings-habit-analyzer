from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import GoalCreate, GoalProgressUpdate, GoalRead
from app.services.goal_service import GoalNotFoundError, GoalService

router = APIRouter()


@router.post(
    "",
    response_model=GoalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create savings goal",
    description="Create a savings goal for the authenticated user.",
)
async def create_goal(
    goal_create: GoalCreate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> GoalRead:
    goal_service = GoalService(GoalRepository(db_session))

    try:
        goal = await goal_service.create_goal(
            user_id=current_user.id,
            goal_create=goal_create,
        )
        await db_session.commit()
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create goal.",
        ) from exc

    return goal


@router.get(
    "",
    response_model=list[GoalRead],
    summary="List savings goals",
    description="Return the authenticated user's goals, optionally filtered by completion status.",
)
async def list_goals(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    is_completed: bool | None = None,
) -> list[GoalRead]:
    goal_service = GoalService(GoalRepository(db_session))
    return await goal_service.list_goals(
        user_id=current_user.id,
        is_completed=is_completed,
    )


@router.patch(
    "/{goal_id}/progress",
    response_model=GoalRead,
    summary="Update goal progress",
    description="Update progress toward an owned savings goal.",
)
async def update_goal_progress(
    goal_id: UUID,
    progress_update: GoalProgressUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> GoalRead:
    goal_service = GoalService(GoalRepository(db_session))

    try:
        goal = await goal_service.update_goal_progress(
            goal_id=goal_id,
            user_id=current_user.id,
            progress_update=progress_update,
        )
        await db_session.commit()
    except GoalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found.",
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update goal progress.",
        ) from exc

    return goal
