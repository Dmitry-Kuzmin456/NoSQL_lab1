from abc import ABC, abstractmethod
from uuid import UUID

from domain.history import OperationEvent


class IHistoryRepository(ABC):
    """Интерфейс репозитория истории операций."""

    @abstractmethod
    def add_event(self, event: OperationEvent) -> None:
        """Зафиксировать новое событие в истории операций."""
        raise NotImplementedError

    @abstractmethod
    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[OperationEvent], int]:
        """Получить срез событий пользователя с пагинацией и общее количество событий."""
        raise NotImplementedError

    @abstractmethod
    def count_user_events(self, user_id: UUID) -> int:
        """Получить общее количество событий пользователя."""
        raise NotImplementedError

    @abstractmethod
    def clear(self, user_id: UUID) -> bool:
        """Очистить историю действий пользователя."""
        raise NotImplementedError
