from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from application.user.dto import (
    ChangePasswordDto,
    UserRegisterDto,
    UserResponseDto,
    UserUpdateDto,
)
from domain.user import UserRole


class RegisterUserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Иван Иванов"])
    email: EmailStr = Field(..., examples=["ivan@edu.ru"])
    password: str = Field(
        ..., min_length=6, max_length=128, examples=["secretPassword123"]
    )
    role: UserRole = Field(default=UserRole.STUDENT, examples=[UserRole.STUDENT])

    def to_dto(self) -> UserRegisterDto:
        return UserRegisterDto(
            name=self.name,
            email=str(self.email),
            password=self.password,
            role=self.role,
        )


class UpdateUserRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None

    def to_dto(self) -> UserUpdateDto:
        return UserUpdateDto(
            name=self.name,
            email=str(self.email) if self.email else None,
        )


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)

    def to_dto(self) -> ChangePasswordDto:
        return ChangePasswordDto(
            old_password=self.old_password,
            new_password=self.new_password,
        )


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole

    @classmethod
    def from_dto(cls, dto: UserResponseDto) -> "UserResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            email=dto.email,
            role=dto.role,
        )
