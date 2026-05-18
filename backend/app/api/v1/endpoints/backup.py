from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.backup import BackupExportResponse, BackupImportRequest, BackupImportResponse
from app.schemas.budget import BudgetCreate
from app.schemas.expense import ExpenseCreate
from app.schemas.goal import GoalCreate
from app.services.budget_service import BudgetService
from app.services.expense_service import ExpenseService
from app.services.goal_service import GoalService

router = APIRouter()


@router.get("/export", response_model=BackupExportResponse, summary="Export user data")
async def export_backup(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> BackupExportResponse:
    expenses = await ExpenseRepository(db_session).list_by_user(
        user_id=current_user.id,
        limit=500,
        offset=0,
    )
    goals = await GoalRepository(db_session).list_by_user(user_id=current_user.id)
    budgets = await BudgetRepository(db_session).list_by_user(user_id=current_user.id)

    return BackupExportResponse(
        exported_at=datetime.now(UTC).isoformat(),
        expenses=[
            {
                "amount": str(expense.amount),
                "category": expense.category,
                "description": expense.description,
                "spent_at": expense.spent_at.isoformat(),
            }
            for expense in expenses
        ],
        goals=[
            {
                "name": goal.name,
                "target_amount": str(goal.target_amount),
                "current_amount": str(goal.current_amount),
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
            }
            for goal in goals
        ],
        budgets=[
            {
                "category": budget.category,
                "monthly_limit": str(budget.monthly_limit),
            }
            for budget in budgets
        ],
    )


@router.post("/import", response_model=BackupImportResponse, summary="Import user data")
async def import_backup(
    import_request: BackupImportRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> BackupImportResponse:
    expense_service = ExpenseService(ExpenseRepository(db_session))
    goal_service = GoalService(GoalRepository(db_session))
    budget_service = BudgetService(BudgetRepository(db_session), ExpenseRepository(db_session))
    imported_expenses = 0
    imported_goals = 0
    imported_budgets = 0
    skipped = 0

    for expense in import_request.payload.expenses:
        expense_create = ExpenseCreate(
            amount=Decimal(str(expense["amount"])),
            category=str(expense["category"]),
            description=expense.get("description"),
            spent_at=datetime.fromisoformat(str(expense["spent_at"])),
        )
        if import_request.skip_duplicates:
            duplicate = await expense_service.check_duplicates(
                user_id=current_user.id,
                expense_create=expense_create,
            )
            if duplicate.has_duplicates:
                skipped += 1
                continue
        await expense_service.create_expense(user_id=current_user.id, expense_create=expense_create)
        imported_expenses += 1

    for goal in import_request.payload.goals:
        await goal_service.create_goal(
            user_id=current_user.id,
            goal_create=GoalCreate(
                name=str(goal["name"]),
                target_amount=Decimal(str(goal["target_amount"])),
                current_amount=Decimal(str(goal.get("current_amount", "0.00"))),
                target_date=goal.get("target_date"),
            ),
        )
        imported_goals += 1

    for budget in import_request.payload.budgets:
        await budget_service.upsert_budget(
            user_id=current_user.id,
            budget_create=BudgetCreate(
                category=str(budget["category"]),
                monthly_limit=Decimal(str(budget["monthly_limit"])),
            ),
        )
        imported_budgets += 1

    await db_session.commit()
    return BackupImportResponse(
        imported_expenses=imported_expenses,
        imported_goals=imported_goals,
        imported_budgets=imported_budgets,
        skipped=skipped,
    )
