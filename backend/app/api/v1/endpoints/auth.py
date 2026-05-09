from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user_service import UserAlreadyExistsError, UserService

router = APIRouter()


def get_user_service(
    db_session: AsyncSession = Depends(get_db_session),
) -> UserService:
    return UserService(UserRepository(db_session))


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Create a new user account with an email, password, and optional name.",
)
async def register_user(
    user_create: UserCreate,
    db_session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    user_service = UserService(UserRepository(db_session))

    try:
        user = await user_service.create_user(user_create)
        await db_session.commit()
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists.",
        ) from exc
    except IntegrityError as exc:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists.",
        ) from exc

    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate a user and return a JWT access token.",
)
async def login_user(
    user_login: UserLogin,
    user_service: UserService = Depends(get_user_service),
) -> Token:
    user = await user_service.authenticate_user(user_login.email, user_login.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Read current user",
    description="Return the authenticated user's profile.",
)
async def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> UserRead:
    return UserRead.model_validate(current_user)
