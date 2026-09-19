import logging
from concurrent.futures import ThreadPoolExecutor
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
    """Композитный репозиторий истории операций с конкурентным выполнением и асинхронным обновлением кэша."""

    def __init__(
        self,
        postgres_repo: PostgresHistoryRepository,
        riak_repo: RiakHistoryCacheRepository,
        cache_capacity: int = 20,
    ) -> None:
        self._postgres_repo = postgres_repo
        self._riak_repo = riak_repo
        self._cache_capacity = cache_capacity
        self._executor = ThreadPoolExecutor(
            max_workers=8,
            thread_name_prefix="history-cache-worker",
        )

    def _refresh_cache(self, user_id: UUID) -> None:
        """Асинхронно обновляет кэш свежими отсортированными данными из PostgreSQL."""
        try:
            recent_events = self._postgres_repo.list_by_user_id(
                user_id=user_id,
                offset=0,
                limit=self._cache_capacity,
            )
            self._riak_repo.set_cached_events(user_id, recent_events)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to async refresh history cache for user %s: %s",
                user_id,
                exc,
            )

    def _invalidate_and_refresh_cache(self, user_id: UUID) -> None:
        """Инвалидирует старый кэш и асинхронно обновляет его свежими данными из PostgreSQL."""
        try:
            self._riak_repo.clear(user_id)
            self._refresh_cache(user_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to async invalidate and refresh history cache for user %s: %s",
                user_id,
                exc,
            )

    def add_event(self, event: OperationEvent) -> None:
        """Сохраняет событие в PostgreSQL и асинхронно инвалидирует/обновляет кэш в Riak."""
        self._postgres_repo.save(event)
        self._executor.submit(self._invalidate_and_refresh_cache, event.user_id)

    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[OperationEvent]:
        """Получить события пользователя."""
        if offset == 0 and limit <= self._cache_capacity:
            cached = self._riak_repo.get_cached_events(user_id, limit=limit)
            if cached is not None:
                return cached

        events = self._postgres_repo.list_by_user_id(
            user_id=user_id,
            offset=offset,
            limit=limit,
        )
        return events

    def clear(self, user_id: UUID) -> bool:
        """Конкурентно очищает историю в PostgreSQL и инвалидирует кэш в Riak."""
        fut_clear = self._executor.submit(self._riak_repo.clear, user_id)
        fut_delete = self._executor.submit(
            self._postgres_repo.delete_by_user_id, user_id
        )

        deleted = fut_delete.result()
        fut_clear.result()
        return deleted
