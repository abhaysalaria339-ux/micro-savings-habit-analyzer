from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.pagination import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT, MAX_PAGE_OFFSET
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate, ExpenseListResponse, ExpenseRead, ExpenseUpdate
from app.services.expense_service import ExpenseNotFoundError, ExpenseService

router = APIRouter()


@router.get(
    "",
    response_model=ExpenseListResponse,
    summary="List expenses",
    description="Return the authenticated user's expenses with filters and pagination metadata.",
)
async def list_expenses(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    offset: Annotated[int, Query(ge=0, le=MAX_PAGE_OFFSET)] = 0,
) -> ExpenseListResponse:
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date.",
        )

    expense_service = ExpenseService(ExpenseRepository(db_session))
    return await expense_service.list_expense_page(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        category=category,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{expense_id}",
    response_model=ExpenseRead,
    summary="Get expense",
    description="Return one owned expense by ID.",
)
async def get_expense(
    expense_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ExpenseRead:
    expense_service = ExpenseService(ExpenseRepository(db_session))

    try:
        return await expense_service.get_expense(
            expense_id=expense_id,
            user_id=current_user.id,
        )
    except ExpenseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        ) from exc


@router.post(
    "",
    response_model=ExpenseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create expense",
    description="Create a manual expense entry for the authenticated user.",
)
async def create_expense(
    expense_create: ExpenseCreate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ExpenseRead:
    expense_service = ExpenseService(ExpenseRepository(db_session))

    try:
        expense = await expense_service.create_expense(
            user_id=current_user.id,
            expense_create=expense_create,
        )
        await db_session.commit()
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create expense.",
        ) from exc

    return ExpenseRead.model_validate(expense)


@router.patch(
    "/{expense_id}",
    response_model=ExpenseRead,
    summary="Update expense",
    description="Partially update an owned expense record.",
)
async def update_expense(
    expense_id: UUID,
    expense_update: ExpenseUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ExpenseRead:
    expense_service = ExpenseService(ExpenseRepository(db_session))

    try:
        expense = await expense_service.update_expense(
            expense_id=expense_id,
            user_id=current_user.id,
            expense_update=expense_update,
        )
        await db_session.commit()
    except ExpenseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update expense.",
        ) from exc

    return expense


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete expense",
    description="Delete an owned expense record.",
)
async def delete_expense(
    expense_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    expense_service = ExpenseService(ExpenseRepository(db_session))

    try:
        await expense_service.delete_expense(
            expense_id=expense_id,
            user_id=current_user.id,
        )
        await db_session.commit()
    except ExpenseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        ) from exc
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete expense.",
        ) from exc
