from uuid import UUID

from app.models.user_settings import UserSettings
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import UserSettingsRead, UserSettingsUpdate


class SettingsService:
    def __init__(self, settings_repository: SettingsRepository) -> None:
        self.settings_repository = settings_repository

    async def get_settings(self, *, user_id: UUID) -> UserSettingsRead:
        settings = await self._get_or_create(user_id=user_id)
        return self.to_read(settings)

    async def update_settings(
        self,
        *,
        user_id: UUID,
        settings_update: UserSettingsUpdate,
    ) -> UserSettingsRead:
        settings = await self._get_or_create(user_id=user_id)
        updated = await self.settings_repository.update(
            settings=settings,
            values=settings_update.model_dump(),
        )
        return self.to_read(updated)

    async def _get_or_create(self, *, user_id: UUID) -> UserSettings:
        settings = await self.settings_repository.get_by_user(user_id=user_id)
        if settings is not None:
            return settings

        return await self.settings_repository.create_default(user_id=user_id)

    def to_read(self, settings: UserSettings) -> UserSettingsRead:
        return UserSettingsRead(
            id=settings.id,
            user_id=settings.user_id,
            currency=settings.currency,
            monthly_income=settings.monthly_income,
            savings_target_percentage=settings.savings_target_percentage,
            email_notifications_enabled=settings.email_notifications_enabled,
            sms_notifications_enabled=settings.sms_notifications_enabled,
            phone_number=settings.phone_number,
            created_at=settings.created_at,
            updated_at=settings.updated_at,
        )
