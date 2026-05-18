from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class UserSettingsUpdate(BaseModel):
    currency: str = Field(default="INR", min_length=3, max_length=3)
    monthly_income: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    savings_target_percentage: Decimal = Field(default=Decimal("20.00"), ge=0, le=100)
    email_notifications_enabled: bool = False
    sms_notifications_enabled: bool = False
    phone_number: str | None = Field(default=None, max_length=32)


class UserSettingsRead(UserSettingsUpdate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
