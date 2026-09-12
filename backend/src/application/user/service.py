from uuid import UUID

from domain.user import User, UserRole

from .dto import (
    ChangePasswordDto,
    UserRegisterDto,
    UserResponseDto,
    UserUpdateDto,
)
from .exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    WeakNewPasswordException,
    WeakPasswordException,
)
from .hasher import IPasswordHasher
from .repository import IUserRepository


class UserService:
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def register(self, dto: UserRegisterDto) -> UserResponseDto:
        normalized_email = dto.email.strip().lower()

        if len(dto.password) < 6:
            raise WeakPasswordException()

        existing_user = self._user_repository.get_by_email(normalized_email)
        if existing_user is not None:
            raise UserAlreadyExistsException(normalized_email)

        hashed_password = self._password_hasher.hash(dto.password)

        user = User(
            name=dto.name.strip(),
            email=normalized_email,
            password_hash=hashed_password,
            role=dto.role,
        )

        saved_user = self._user_repository.save(user)
        return UserResponseDto.from_domain(saved_user)

    def get_by_id(self, user_id: UUID) -> UserResponseDto:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return UserResponseDto.from_domain(user)

    def get_by_email(self, email: str) -> UserResponseDto:
        normalized_email = email.strip().lower()
        user = self._user_repository.get_by_email(normalized_email)
        if user is None:
            raise UserNotFoundException(normalized_email)
        return UserResponseDto.from_domain(user)

    def update_profile(self, user_id: UUID, dto: UserUpdateDto) -> UserResponseDto:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)

        if dto.email is not None:
            new_email = dto.email.strip().lower()
            if new_email != user.email:
                existing = self._user_repository.get_by_email(new_email)
                if existing is not None:
                    raise UserAlreadyExistsException(new_email)
                user.email = new_email

        if dto.name is not None:
            user.name = dto.name.strip()

        saved_user = self._user_repository.save(user)
        return UserResponseDto.from_domain(saved_user)

    def change_password(self, user_id: UUID, dto: ChangePasswordDto) -> None:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)

        if not self._password_hasher.verify(dto.old_password, user.password_hash):
            raise InvalidCredentialsException()

        if len(dto.new_password) < 6:
            raise WeakNewPasswordException()

        user.password_hash = self._password_hasher.hash(dto.new_password)
        self._user_repository.save(user)

    def delete_user(self, user_id: UUID) -> bool:
        if self._user_repository.get_by_id(user_id) is None:
            raise UserNotFoundException(user_id)
        return self._user_repository.delete(user_id)
