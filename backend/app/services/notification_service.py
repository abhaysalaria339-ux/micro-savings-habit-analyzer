from uuid import UUID

from app.repositories.notification_repository import NotificationRepository
from app.schemas.alert import SpendingAlert
from app.schemas.notification import (
    NotificationListResponse,
    NotificationRead,
    NotificationSyncResponse,
)


class NotificationService:
    def __init__(self, notification_repository: NotificationRepository) -> None:
        self.notification_repository = notification_repository

    async def list_notifications(self, *, user_id: UUID) -> NotificationListResponse:
        notifications = await self.notification_repository.list_by_user(user_id=user_id)
        unread_count = await self.notification_repository.count_unread(user_id=user_id)
        return NotificationListResponse(
            items=[self.to_read(notification) for notification in notifications],
            unread_count=unread_count,
        )

    async def sync_from_alerts(
        self,
        *,
        user_id: UUID,
        alerts: list[SpendingAlert],
    ) -> NotificationSyncResponse:
        created = []
        for alert in alerts:
            existing = await self.notification_repository.find_recent_similar(
                user_id=user_id,
                title=alert.title,
                notification_type=alert.alert_type,
            )
            if existing is not None:
                continue

            notification = await self.notification_repository.create(
                user_id=user_id,
                notification_type=alert.alert_type,
                severity=alert.severity,
                channel="in_app",
                delivery_status="sent",
                title=alert.title,
                message=alert.nudge,
            )
            created.append(notification)

        return NotificationSyncResponse(
            created_count=len(created),
            items=[self.to_read(notification) for notification in created],
        )

    async def mark_all_read(self, *, user_id: UUID) -> None:
        await self.notification_repository.mark_all_read(user_id=user_id)

    def to_read(self, notification) -> NotificationRead:
        return NotificationRead(
            id=notification.id,
            notification_type=notification.notification_type,
            severity=notification.severity,
            channel=notification.channel,
            delivery_status=notification.delivery_status,
            title=notification.title,
            message=notification.message,
            is_read=notification.is_read,
            read_at=notification.read_at,
            created_at=notification.created_at,
        )
