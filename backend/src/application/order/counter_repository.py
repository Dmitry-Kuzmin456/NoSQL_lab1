from abc import ABC, abstractmethod
from uuid import UUID


class IOrderCounterRepository(ABC):
    """Интерфейс счетчика заказов."""

    @abstractmethod
    def increment(self, user_id: UUID, amount: int = 1) -> int:
        """Инкрементировать счетчик заказов пользователя."""
        raise NotImplementedError

    @abstractmethod
    def decrement(self, user_id: UUID, amount: int = 1) -> int:
        """Декрементировать счетчик заказов пользователя."""
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> int:
        """Получить количество заказов пользователя."""
        raise NotImplementedError

    @abstractmethod
    def get_total_count(self) -> int:
        """Получить общее количество заказов."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить счетчик заказов пользователя."""
        raise NotImplementedError
