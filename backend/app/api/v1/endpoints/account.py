from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserPasswordUpdate, UserProfileUpdate, UserRead
from app.services.user_service import InvalidCurrentPasswordError, UserService

router = APIRouter()


@router.patch("/profile", response_model=UserRead, summary="Update profile")
async def update_profile(
    profile_update: UserProfileUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserRead:
    service = UserService(UserRepository(db_session))
    user = await service.update_profile(user=current_user, profile_update=profile_update)
    await db_session.commit()
    return UserRead.model_validate(user)


@router.patch("/password", status_code=204, summary="Change password")
async def update_password(
    password_update: UserPasswordUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = UserService(UserRepository(db_session))
    try:
        await service.update_password(user=current_user, password_update=password_update)
        await db_session.commit()
    except InvalidCurrentPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is invalid.",
        ) from exc


@router.delete("", status_code=204, summary="Delete account")
async def delete_account(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = UserService(UserRepository(db_session))
    try:
        await service.delete_account(user=current_user)
        await db_session.commit()
    except SQLAlchemyError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete account.",
        ) from exc
