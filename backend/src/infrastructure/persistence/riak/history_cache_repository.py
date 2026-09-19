from datetime import datetime
from typing import Any
from uuid import UUID

from domain.history import OperationEvent, OperationType
from infrastructure.persistence.riak.client import (
    RiakClient,
    RiakObject,
    get_riak_client,
)


class RiakHistoryCacheRepository:
    """Кэш-репозиторий истории для Riak KV."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "history_cache",
        bucket_type: str = "default",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._bucket_type = bucket_type

    @staticmethod
    def _event_to_dict(event: OperationEvent) -> dict[str, Any]:
        return {
            "id": str(event.id),
            "user_id": str(event.user_id),
            "action": event.action.value,
            "target_id": str(event.target_id) if event.target_id else None,
            "details": event.details,
            "timestamp": event.timestamp.isoformat(),
        }

    @staticmethod
    def _dict_to_event(data: dict[str, Any]) -> OperationEvent:
        return OperationEvent(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            action=OperationType(data["action"]),
            target_id=UUID(data["target_id"]) if data.get("target_id") else None,
            details=data.get("details", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )

    def set_cached_events(self, user_id: UUID, events: list[OperationEvent]) -> None:
        """Сохранить события в кэш в отсортированном по убыванию времени виде."""
        sorted_events = sorted(events, key=lambda e: e.timestamp, reverse=True)
        payload = {
            "user_id": str(user_id),
            "events": [self._event_to_dict(e) for e in sorted_events],
        }
        obj = RiakObject(
            bucket=self._bucket,
            key=str(user_id),
            data=payload,
            bucket_type=self._bucket_type,
            vclock=None,
        )
        self._client.put(obj)

    def get_cached_events(
        self, user_id: UUID, limit: int = 20
    ) -> list[OperationEvent] | None:
        """Получить события из кэша"""
        obj = self._client.get(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
        if obj is None or not isinstance(obj.data, dict):
            return None

        raw_events = obj.data.get("events", [])
        events = [self._dict_to_event(item) for item in raw_events]
        return events[:limit]

    def clear(self, user_id: UUID) -> bool:
        """Инвалидировать/очистить кэш истории пользователя."""
        return self._client.delete(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
