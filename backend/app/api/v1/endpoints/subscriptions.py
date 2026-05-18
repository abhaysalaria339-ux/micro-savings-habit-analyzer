from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.subscription import SubscriptionDetectionResponse
from app.services.subscription_service import SubscriptionService

router = APIRouter()


@router.get("", response_model=SubscriptionDetectionResponse, summary="Detect subscriptions")
async def detect_subscriptions(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> SubscriptionDetectionResponse:
    service = SubscriptionService(ExpenseRepository(db_session))
    return await service.detect_subscriptions(user_id=current_user.id)
