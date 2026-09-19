import logging
from uuid import UUID

from application.history.repository import IHistoryRepository
from domain.history import OperationEvent
from infrastructure.persistence.postgres.history_repository import (
    PostgresHistoryRepository,
)
from infrastructure.persistence.riak.history_cache_repository import (
    RiakHistoryCacheRepository,
)

logger = logging.getLogger(__name__)


class CompositeHistoryRepository(IHistoryRepository):
    """Композитный репозиторий истории операций с кэшированием в Riak KV (Cache-Aside)."""

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
        """Сохраняет событие в PostgreSQL и инвалидирует кэш в Riak."""
        self._postgres_repo.save(event)
        try:
            self._riak_repo.clear(event.user_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to invalidate history cache for user %s: %s", event.user_id, exc)

    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[OperationEvent]:
        """Получить события пользователя из кэша Riak (если есть) или из PostgreSQL."""
        if offset == 0 and limit <= self._cache_capacity:
            try:
                cached = self._riak_repo.get_cached_events(user_id, limit=limit)
                if cached is not None:
                    return cached
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to read history cache for user %s: %s", user_id, exc)

        events = self._postgres_repo.list_by_user_id(
            user_id=user_id,
            offset=offset,
            limit=limit,
        )

        if offset == 0:
            try:
                self._riak_repo.set_cached_events(user_id, events)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to populate history cache for user %s: %s", user_id, exc)

        return events

    def clear(self, user_id: UUID) -> bool:
        """Очищает историю в PostgreSQL и инвалидирует кэш в Riak."""
        deleted = self._postgres_repo.delete_by_user_id(user_id)
        try:
            self._riak_repo.clear(user_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to clear history cache for user %s: %s", user_id, exc)
        return deleted
