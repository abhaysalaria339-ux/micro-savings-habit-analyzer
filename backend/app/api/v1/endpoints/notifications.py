from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationListResponse, NotificationSyncResponse
from app.services.alert_service import AlertService
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=NotificationListResponse, summary="List notifications")
async def list_notifications(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> NotificationListResponse:
    service = NotificationService(NotificationRepository(db_session))
    return await service.list_notifications(user_id=current_user.id)


@router.post("/sync", response_model=NotificationSyncResponse, summary="Sync alerts")
async def sync_notifications(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> NotificationSyncResponse:
    alert_service = AlertService(ExpenseRepository(db_session), BudgetRepository(db_session))
    alerts = await alert_service.get_spending_alerts(user_id=current_user.id)
    service = NotificationService(NotificationRepository(db_session))
    result = await service.sync_from_alerts(user_id=current_user.id, alerts=alerts.alerts)
    await db_session.commit()
    return result


@router.post("/read-all", status_code=204, summary="Mark notifications read")
async def mark_notifications_read(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = NotificationService(NotificationRepository(db_session))
    await service.mark_all_read(user_id=current_user.id)
    await db_session.commit()
