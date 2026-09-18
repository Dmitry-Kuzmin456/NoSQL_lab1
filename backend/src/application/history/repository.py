from abc import ABC, abstractmethod
from uuid import UUID

from domain.history import OperationEvent


class IHistoryRepository(ABC):
    """Интерфейс репозитория истории операций (композитный фасад)."""

    @abstractmethod
    def append_event(self, event: OperationEvent, max_capacity: int = 20) -> None:
        """Добавить событие в историю и обновить кэш Riak KV."""
        raise NotImplementedError

    @abstractmethod
    def add_event(self, event: OperationEvent) -> None:
        """Атомарно зафиксировать событие (сохранение в PostgreSQL + обновление кэша в Riak KV)."""
        raise NotImplementedError

    @abstractmethod
    def get_cached_user_events(
        self,
        user_id: UUID,
        limit: int = 20,
    ) -> list[OperationEvent]:
        """Метод кэширования: прямое O(1) перенаправление запроса в Riak KV."""
        raise NotImplementedError

    @abstractmethod
    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[OperationEvent], int]:
        """Получить события пользователя (для offset=0 перенаправляется на кэш Riak KV)."""
        raise NotImplementedError

    @abstractmethod
    def count_user_events(self, user_id: UUID) -> int:
        """Получить общее количество событий пользователя."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Проверить наличие хотя бы одного события у пользователя."""
        raise NotImplementedError

    @abstractmethod
    def clear_user_history(self, user_id: UUID) -> bool:
        """Очистить историю пользователя в PostgreSQL и Riak KV."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить историю действий пользователя."""
        raise NotImplementedError
