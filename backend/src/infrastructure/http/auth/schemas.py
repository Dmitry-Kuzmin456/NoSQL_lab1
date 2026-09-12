from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from application.auth.dto import AuthResponseDto, LoginDto
from application.session.dto import SessionResponseDto
from infrastructure.http.user.schemas import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["ivan@edu.ru"])
    password: str = Field(..., min_length=1, examples=["secretPassword123"])

    def to_dto(self) -> LoginDto:
        return LoginDto(
            email=str(self.email),
            password=self.password,
        )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    refresh_token: str
    created_at: datetime
    expires_at: datetime | None = None
    is_revoked: bool

    @classmethod
    def from_dto(cls, dto: SessionResponseDto) -> "SessionResponse":
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            refresh_token=dto.refresh_token,
            created_at=dto.created_at,
            expires_at=dto.expires_at,
            is_revoked=dto.is_revoked,
        )


class AuthResponse(BaseModel):
    user: UserResponse
    session: SessionResponse

    @classmethod
    def from_dto(cls, dto: AuthResponseDto) -> "AuthResponse":
        return cls(
            user=UserResponse.from_dto(dto.user),
            session=SessionResponse.from_dto(dto.session),
        )
