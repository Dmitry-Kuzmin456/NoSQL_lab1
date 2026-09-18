import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import UUID


@dataclass
class RecoveryToken:
    user_id: UUID
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(UTC) + timedelta(minutes=15)
    )

    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at
