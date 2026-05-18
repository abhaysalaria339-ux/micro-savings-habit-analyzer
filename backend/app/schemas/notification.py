from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: UUID
    notification_type: str
    severity: Literal["info", "warning", "critical"]
    channel: Literal["in_app", "email", "sms"]
    delivery_status: Literal["pending", "sent", "failed"]
    title: str
    message: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationRead]
    unread_count: int


class NotificationSyncResponse(BaseModel):
    created_count: int
    items: list[NotificationRead]
