from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.services.budget_service import BudgetNotFoundError, BudgetService

router = APIRouter()


@router.get(
    "",
    response_model=list[BudgetRead],
    summary="List budgets",
    description="Return monthly category budgets with current month usage.",
)
async def list_budgets(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> list[BudgetRead]:
    service = _build_service(db_session)
    return await service.list_budgets(user_id=current_user.id)


@router.post(
    "",
    response_model=BudgetRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update budget",
    description="Create a monthly category budget or update the existing category budget.",
)
async def upsert_budget(
    budget_create: BudgetCreate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> BudgetRead:
    service = _build_service(db_session)

    try:
        budget = await service.upsert_budget(
            user_id=current_user.id,
            budget_create=budget_create,
        )
        await db_session.commit()
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save budget.",
        ) from exc

    return budget


@router.patch(
    "/{budget_id}",
    response_model=BudgetRead,
    summary="Update budget",
    description="Update an owned monthly category budget.",
)
async def update_budget(
    budget_id: UUID,
    budget_update: BudgetUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> BudgetRead:
    service = _build_service(db_session)

    try:
        budget = await service.update_budget(
            budget_id=budget_id,
            user_id=current_user.id,
            budget_update=budget_update,
        )
        await db_session.commit()
    except BudgetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found.",
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update budget.",
        ) from exc

    return budget


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete budget",
    description="Delete an owned monthly category budget.",
)
async def delete_budget(
    budget_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = _build_service(db_session)

    try:
        await service.delete_budget(budget_id=budget_id, user_id=current_user.id)
        await db_session.commit()
    except BudgetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found.",
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete budget.",
        ) from exc


def _build_service(db_session: AsyncSession) -> BudgetService:
    return BudgetService(
        budget_repository=BudgetRepository(db_session),
        expense_repository=ExpenseRepository(db_session),
    )
