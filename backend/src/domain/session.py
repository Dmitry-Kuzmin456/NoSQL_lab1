from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class Session:
    user_id: UUID
    refresh_token: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    is_revoked: bool = False

    def is_expired(self) -> bool:
        if self.is_revoked:
            return True
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def revoke(self) -> None:
        self.is_revoked = True

    def rotate_refresh_token(
        self, new_token: str, new_expires_at: datetime | None = None
    ) -> None:
        self.refresh_token = new_token
        if new_expires_at is not None:
            self.expires_at = new_expires_at
