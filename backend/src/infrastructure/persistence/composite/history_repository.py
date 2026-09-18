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
    """Композитный репозиторий истории операций:

    - PostgresHistoryRepository выступает в роли System of Record для персистентного хранения всех событий.
    - RiakHistoryCacheRepository выступает в роли быстрого кэша последних операций (Capped Ring-Buffer).
    - Метод get_cached_user_events перенаправляет чтение напрямую в Riak KV.
    """

    def __init__(
        self,
        postgres_repo: PostgresHistoryRepository,
        riak_repo: RiakHistoryCacheRepository,
    ) -> None:
        self._postgres_repo = postgres_repo
        self._riak_repo = riak_repo

    def append_event(self, event: OperationEvent, max_capacity: int = 20) -> None:
        """Сохранение в PostgreSQL + обновление кэша в Riak KV."""
        self._postgres_repo.save(event)
        self._riak_repo.append_event(event, max_capacity=max_capacity)

    def add_event(self, event: OperationEvent) -> None:
        """Сохранение в PostgreSQL + обновление кэша в Riak KV."""
        self.append_event(event, max_capacity=20)

    def get_cached_user_events(
        self,
        user_id: UUID,
        limit: int = 20,
    ) -> list[OperationEvent]:
        """Специализированный метод кэширования: прямое перенаправление в Riak KV."""
        return self._riak_repo.get_cached_events(user_id=user_id, limit=limit)

    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[OperationEvent], int]:
        """Получить события пользователя (для offset=0 срез берется из Riak KV)."""
        raise NotImplementedError

    def count_user_events(self, user_id: UUID) -> int:
        raise NotImplementedError

    def exists_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def clear_user_history(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def delete_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError
