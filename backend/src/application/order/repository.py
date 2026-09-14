from abc import ABC, abstractmethod
from uuid import UUID

from domain.order import Order, OrderStatus

from .dto import OrderFilterDto


class IOrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Order | None:
        """Получить заказ по ID."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, order_id: UUID) -> bool:
        """Проверить существование заказа по ID без загрузки его полей."""
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
    def update_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        expected_status: OrderStatus | None = None,
    ) -> bool:
        """
        Атомарно обновить статус заказа без предварительной загрузки сущности.
        Если указан expected_status, обновление выполняется только если текущий статус равен expected_status.
        Возвращает True в случае успешной модификации, False если заказ не найден или статус не совпал.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, order_id: UUID) -> bool:
        """Удалить заказ по ID."""
        raise NotImplementedError

    @abstractmethod
    def increment_orders_count(self, amount: int = 1) -> int:
        """
        Атомарно инкрементировать глобальный счётчик созданных заявок (Riak PN-Counter).
        Возвращает новое значение счётчика.
        """
        raise NotImplementedError

    @abstractmethod
    def get_total_orders_count(self) -> int:
        """Получить текущее значение атомарного счётчика созданных заявок."""
        raise NotImplementedError
