from abc import ABC, abstractmethod
from uuid import UUID

from domain.history import OperationEvent


class IHistoryRepository(ABC):
    @abstractmethod
    def add_event(self, event: OperationEvent) -> None:
        """Атомарно добавить новое событие в историю БЕЗ предварительного чтения всех событий."""
        raise NotImplementedError

    @abstractmethod
    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[OperationEvent], int]:
        """Получить срез событий пользователя с пагинацией (offset, limit) и общее количество событий."""
        raise NotImplementedError

    @abstractmethod
    def count_user_events(self, user_id: UUID) -> int:
        """Быстро получить общее количество событий пользователя без вычитки всех записей."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Проверить наличие хотя бы одного события у пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить историю действий пользователя."""
        raise NotImplementedError
