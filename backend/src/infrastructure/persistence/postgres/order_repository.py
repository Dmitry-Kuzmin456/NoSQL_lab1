from uuid import UUID

from application.order.dto import OrderFilterDto
from application.order.repository import IOrderRepository
from domain.order import Order, OrderStatus


class PostgresOrderRepository(IOrderRepository):
    """Репозиторий заказов для PostgreSQL."""

    def get_by_id(self, order_id: UUID) -> Order | None:
        raise NotImplementedError

    def exists_by_id(self, order_id: UUID) -> bool:
        raise NotImplementedError

    def get_by_user_id(self, user_id: UUID) -> list[Order]:
        raise NotImplementedError

    def list(
        self,
        filter_dto: OrderFilterDto | None = None,
    ) -> tuple[list[Order], int]:
        raise NotImplementedError

    def save(self, order: Order) -> Order:
        raise NotImplementedError

    def update_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        expected_status: OrderStatus | None = None,
    ) -> bool:
        raise NotImplementedError
