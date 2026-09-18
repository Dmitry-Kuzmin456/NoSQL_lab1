from uuid import UUID

from domain.history import OperationEvent


class RiakHistoryCacheRepository:
    """Реализация кэша истории операций на базе Riak KV (Capped Ring-Buffer по ключу user_id)."""

    def append_event(self, event: OperationEvent, max_capacity: int = 20) -> None:
        raise NotImplementedError

    def get_cached_events(self, user_id: UUID, limit: int = 20) -> list[OperationEvent]:
        raise NotImplementedError

    def clear(self, user_id: UUID) -> bool:
        raise NotImplementedError
