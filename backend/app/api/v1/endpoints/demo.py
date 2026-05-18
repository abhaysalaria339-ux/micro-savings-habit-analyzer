from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.budget import Budget
from app.models.expense import Expense
from app.models.goal import Goal
from app.models.notification import Notification
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseRead

router = APIRouter()


@router.post("/seed", response_model=list[ExpenseRead], summary="Seed demo data")
async def seed_demo_data(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> list[ExpenseRead]:
    repository = ExpenseRepository(db_session)
    now = datetime.now(UTC)
    rows = [
        (Decimal("80.00"), "Coffee", "Morning coffee"),
        (Decimal("50.00"), "Snacks", "Small snack purchase"),
        (Decimal("120.00"), "Transport", "Short ride"),
        (Decimal("1200.00"), "Subscription", "Spotify subscription"),
        (Decimal("2500.00"), "Shopping", "Weekend shopping"),
    ]
    created = []
    for index in range(45):
        amount, category, description = rows[index % len(rows)]
        created.append(
            await repository.create(
                user_id=current_user.id,
                amount=amount,
                category=category,
                description=description,
                spent_at=now - timedelta(days=index),
            )
        )

    await db_session.commit()
    return [ExpenseRead.model_validate(expense) for expense in created]


@router.delete("/reset", status_code=204, summary="Reset demo data")
async def reset_demo_data(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    for model in (Notification, Expense, Goal, Budget):
        await db_session.execute(delete(model).where(model.user_id == current_user.id))
    await db_session.commit()
