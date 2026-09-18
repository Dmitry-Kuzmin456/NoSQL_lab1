from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.recovery_token import RecoveryToken


@dataclass(frozen=True)
class CreateRecoveryDto:
    email: str


@dataclass(frozen=True)
class RecoveryResponseDto:
    token: str
    user_id: UUID
    created_at: datetime
    expires_at: datetime
    is_expired: bool

    @classmethod
    def from_domain(cls, recovery_token: RecoveryToken) -> "RecoveryResponseDto":
        return cls(
            token=recovery_token.token,
            user_id=recovery_token.user_id,
            created_at=recovery_token.created_at,
            expires_at=recovery_token.expires_at,
            is_expired=recovery_token.is_expired(),
        )


@dataclass(frozen=True)
class ResetPasswordWithTokenDto:
    token: str
    new_password: str
