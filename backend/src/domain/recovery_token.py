import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID


@dataclass
class RecoveryToken:
    user_id: UUID
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    is_used: bool = False

    def is_expired(self) -> bool:
        if self.is_used:
            return True
        return datetime.now(timezone.utc) > self.expires_at

    def mark_as_used(self) -> None:
        self.is_used = True
