from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserPasswordUpdate, UserProfileUpdate


class UserAlreadyExistsError(Exception):
    pass


class InvalidCurrentPasswordError(Exception):
    pass


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def create_user(self, user_create: UserCreate) -> User:
        existing_user = await self.user_repository.get_by_email(user_create.email)
        if existing_user is not None:
            raise UserAlreadyExistsError("User with this email already exists.")

        return await self.user_repository.create(
            email=user_create.email,
            hashed_password=hash_password(user_create.password),
            full_name=user_create.full_name,
        )

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.user_repository.get_by_email(email)
        if user is None:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def update_profile(
        self,
        *,
        user: User,
        profile_update: UserProfileUpdate,
    ) -> User:
        return await self.user_repository.update(
            user=user,
            values=profile_update.model_dump(exclude_unset=True),
        )

    async def update_password(
        self,
        *,
        user: User,
        password_update: UserPasswordUpdate,
    ) -> None:
        if not verify_password(password_update.current_password, user.hashed_password):
            raise InvalidCurrentPasswordError("Current password is invalid.")

        await self.user_repository.update(
            user=user,
            values={"hashed_password": hash_password(password_update.new_password)},
        )

    async def delete_account(self, *, user: User) -> None:
        await self.user_repository.delete(user=user)
