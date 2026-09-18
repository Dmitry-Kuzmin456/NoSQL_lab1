from uuid import UUID

from application.history.repository import IHistoryRepository
from domain.history import OperationEvent
from infrastructure.persistence.postgres.history_repository import (
    PostgresHistoryRepository,
)
from infrastructure.persistence.riak.history_cache_repository import (
    RiakHistoryCacheRepository,
)


class CompositeHistoryRepository(IHistoryRepository):
    """Композитный репозиторий истории операций."""

    def __init__(
        self,
        postgres_repo: PostgresHistoryRepository,
        riak_repo: RiakHistoryCacheRepository,
        cache_capacity: int = 20,
    ) -> None:
        self._postgres_repo = postgres_repo
        self._riak_repo = riak_repo
        self._cache_capacity = cache_capacity

    def add_event(self, event: OperationEvent) -> None:
        """Сохранение в PostgreSQL + прозрачное обновление кэша в Riak KV."""
        self._postgres_repo.save(event)
        self._riak_repo.append_event(event, max_capacity=self._cache_capacity)

    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[OperationEvent], int]:
        """Прозрачное чтение из кэша Riak KV при offset=0 с обращением к PostgreSQL при пагинации."""
        total = self._postgres_repo.count_by_user_id(user_id)
        if offset == 0:
            cached = self._riak_repo.get_cached_events(user_id, limit=limit)
            if cached:
                return cached, total

        events, total = self._postgres_repo.list_by_user_id(
            user_id=user_id, offset=offset, limit=limit
        )
        return events, total

    def count_user_events(self, user_id: UUID) -> int:
        return self._postgres_repo.count_by_user_id(user_id)

    def clear_user_history(self, user_id: UUID) -> bool:
        self._riak_repo.clear(user_id)
        return self._postgres_repo.delete_by_user_id(user_id)

    def delete_by_user_id(self, user_id: UUID) -> bool:
        self._riak_repo.clear(user_id)
        return self._postgres_repo.delete_by_user_id(user_id)
