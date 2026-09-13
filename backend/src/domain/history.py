from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class OperationType(StrEnum):
    VIEW_PRODUCT = "VIEW_PRODUCT"
    ADD_FAVOURITE = "ADD_FAVOURITE"
    REMOVE_FAVOURITE = "REMOVE_FAVOURITE"
    CREATE_ORDER = "CREATE_ORDER"
    CANCEL_ORDER = "CANCEL_ORDER"
    PASSWORD_RESET = "PASSWORD_RESET"


@dataclass
class OperationEvent:
    user_id: UUID
    action: OperationType
    target_id: UUID | None = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: UUID = field(default_factory=uuid4)


@dataclass
class UserHistory:
    user_id: UUID
    events: list[OperationEvent] = field(default_factory=list)

    def add_event(self, event: OperationEvent, max_size: int = 20) -> None:
        self.events.insert(0, event)
        self.events = sorted(self.events, key=lambda e: e.timestamp, reverse=True)[
            :max_size
        ]

    def get_recent_events(self, limit: int = 10) -> list[OperationEvent]:
        return sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:limit]
