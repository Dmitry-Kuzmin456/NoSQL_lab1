from abc import ABC, abstractmethod
from uuid import UUID

from domain.order import Order, OrderStatus

from .dto import OrderFilterDto


class IOrderRepository(ABC):
    """Интерфейс репозитория заказов."""

    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Order | None:
        """Получить заказ по ID."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, order_id: UUID) -> bool:
        """Проверить существование заказа."""
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> list[Order]:
        """Получить заказы пользователя."""
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        filter_dto: OrderFilterDto | None = None,
    ) -> list[Order]:
        """Получить список заказов с фильтрацией."""
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> Order:
        """Сохранить заказ."""
        raise NotImplementedError

    @abstractmethod
    def update_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        expected_status: OrderStatus | None = None,
    ) -> bool:
        """Обновить статус заказа."""
        raise NotImplementedError
