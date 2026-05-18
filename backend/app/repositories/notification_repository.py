from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(
        self,
        *,
        user_id: UUID,
        notification_type: str,
        severity: str,
        channel: str,
        delivery_status: str,
        title: str,
        message: str,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            severity=severity,
            channel=channel,
            delivery_status=delivery_status,
            title=title,
            message=message,
            is_read=False,
        )
        self.db_session.add(notification)
        await self.db_session.flush()
        await self.db_session.refresh(notification)
        return notification

    async def list_by_user(
        self,
        *,
        user_id: UUID,
        limit: int = 30,
    ) -> list[Notification]:
        query: Select[tuple[Notification]] = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def count_unread(self, *, user_id: UUID) -> int:
        result = await self.db_session.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        return int(result.scalar_one())

    async def find_recent_similar(
        self,
        *,
        user_id: UUID,
        title: str,
        notification_type: str,
    ) -> Notification | None:
        since = datetime.now(UTC) - timedelta(hours=24)
        result = await self.db_session.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.title == title,
                Notification.notification_type == notification_type,
                Notification.created_at >= since,
            )
        )
        return result.scalar_one_or_none()

    async def mark_all_read(self, *, user_id: UUID) -> None:
        notifications = await self.list_by_user(user_id=user_id, limit=200)
        now = datetime.now(UTC)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
        await self.db_session.flush()
