from abc import ABC, abstractmethod
from uuid import UUID

from domain.order import Order

from .dto import OrderFilterDto


class IOrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Order | None:
        """Получить заказ по ID."""
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> list[Order]:
        """Получить все заказы пользователя по user_id."""
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        filter_dto: OrderFilterDto | None = None,
    ) -> tuple[list[Order], int]:
        """Получить список заказов с фильтрацией и пагинацией."""
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> Order:
        """Сохранить или обновить заказ."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, order_id: UUID) -> bool:
        """Удалить заказ по ID."""
        raise NotImplementedError
