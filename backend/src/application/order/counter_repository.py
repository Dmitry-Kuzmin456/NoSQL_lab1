from abc import ABC, abstractmethod
from uuid import UUID


class IOrderCounterRepository(ABC):
    """Специализированный интерфейс счетчика заказов пользователей на базе Riak PN-Counter CRDT."""

    @abstractmethod
    def increment(self, user_id: UUID, amount: int = 1) -> int:
        """Атомарно инкрементировать счетчик созданных заказов конкретного пользователя (O(1))."""
        raise NotImplementedError

    @abstractmethod
    def decrement(self, user_id: UUID, amount: int = 1) -> int:
        """Атомарно декрементировать счетчик заказов пользователя (O(1))."""
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> int:
        """Получить текущее количество созданных заказов конкретного пользователя (O(1))."""
        raise NotImplementedError

    @abstractmethod
    def get_total_count(self) -> int:
        """Получить суммарное количество заказов по всем пользователям."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить счетчик заказов пользователя (DELETE /counters/{user_id})."""
        raise NotImplementedError


# Псевдоним для обратной совместимости
ICounterRepository = IOrderCounterRepository
