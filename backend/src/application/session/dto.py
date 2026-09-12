from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.session import Session


@dataclass(frozen=True)
class SessionResponseDto:
    id: UUID
    user_id: UUID
    refresh_token: str
    created_at: datetime
    expires_at: datetime | None
    is_revoked: bool

    @classmethod
    def from_domain(cls, session: Session) -> "SessionResponseDto":
        return cls(
            id=session.id,
            user_id=session.user_id,
            refresh_token=session.refresh_token,
            created_at=session.created_at,
            expires_at=session.expires_at,
            is_revoked=session.is_revoked,
        )
