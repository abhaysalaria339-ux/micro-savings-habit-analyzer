from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import UserSettingsRead, UserSettingsUpdate
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get("", response_model=UserSettingsRead, summary="Get user settings")
async def get_settings(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsRead:
    service = SettingsService(SettingsRepository(db_session))
    return await service.get_settings(user_id=current_user.id)


@router.put("", response_model=UserSettingsRead, summary="Update user settings")
async def update_settings(
    settings_update: UserSettingsUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsRead:
    service = SettingsService(SettingsRepository(db_session))
    settings = await service.update_settings(
        user_id=current_user.id,
        settings_update=settings_update,
    )
    await db_session.commit()
    return settings
