from dataclasses import dataclass
from uuid import UUID

from domain.user import User, UserRole


@dataclass(frozen=True)
class UserRegisterDto:
    name: str
    email: str
    password: str
    role: UserRole = UserRole.STUDENT


@dataclass(frozen=True)
class UserLoginDto:
    email: str
    password: str


@dataclass(frozen=True)
class UserUpdateDto:
    name: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class ChangePasswordDto:
    old_password: str
    new_password: str


@dataclass(frozen=True)
class UserResponseDto:
    id: UUID
    name: str
    email: str
    role: UserRole

    @classmethod
    def from_domain(cls, user: User) -> "UserResponseDto":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
        )


@dataclass(frozen=True)
class UserWithPasswordDto:
    id: UUID
    name: str
    email: str
    password_hash: str
    role: UserRole

    @classmethod
    def from_domain(cls, user: User) -> "UserWithPasswordDto":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
        )

    def to_response_dto(self) -> UserResponseDto:
        return UserResponseDto(
            id=self.id,
            name=self.name,
            email=self.email,
            role=self.role,
        )
