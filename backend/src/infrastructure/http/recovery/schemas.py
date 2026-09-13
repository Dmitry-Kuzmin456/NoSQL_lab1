from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from application.recovery.dto import (
    CreateRecoveryDto,
    RecoveryResponseDto,
    ResetPasswordWithTokenDto,
)


class RequestRecoveryRequest(BaseModel):
    email: EmailStr = Field(..., examples=["ivan@edu.ru"])

    def to_dto(self) -> CreateRecoveryDto:
        return CreateRecoveryDto(email=str(self.email))


class ResetPasswordWithTokenRequest(BaseModel):
    token: str = Field(..., min_length=1, examples=["some-recovery-token"])
    new_password: str = Field(
        ..., min_length=6, max_length=128, examples=["newStrongPassword123"]
    )

    def to_dto(self) -> ResetPasswordWithTokenDto:
        return ResetPasswordWithTokenDto(
            token=self.token,
            new_password=self.new_password,
        )


class RecoveryResponse(BaseModel):
    token: str
    user_id: UUID
    created_at: datetime
    expires_at: datetime
    is_used: bool
    is_expired: bool

    @classmethod
    def from_dto(cls, dto: RecoveryResponseDto) -> "RecoveryResponse":
        return cls(
            token=dto.token,
            user_id=dto.user_id,
            created_at=dto.created_at,
            expires_at=dto.expires_at,
            is_used=dto.is_used,
            is_expired=dto.is_expired,
        )


class MessageResponse(BaseModel):
    message: str
