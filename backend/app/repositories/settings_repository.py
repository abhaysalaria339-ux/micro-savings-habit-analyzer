from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_settings import UserSettings


class SettingsRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_by_user(self, *, user_id: UUID) -> UserSettings | None:
        result = await self.db_session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_default(self, *, user_id: UUID) -> UserSettings:
        settings = UserSettings(
            user_id=user_id,
            currency="INR",
            monthly_income=None,
            savings_target_percentage=Decimal("20.00"),
            email_notifications_enabled=False,
            sms_notifications_enabled=False,
            phone_number=None,
        )
        self.db_session.add(settings)
        await self.db_session.flush()
        await self.db_session.refresh(settings)
        return settings

    async def update(self, *, settings: UserSettings, values: dict) -> UserSettings:
        for key, value in values.items():
            setattr(settings, key, value)
        await self.db_session.flush()
        await self.db_session.refresh(settings)
        return settings
