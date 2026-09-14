import copy
import threading
from uuid import UUID

from application.order.dto import OrderFilterDto
from application.order.repository import IOrderRepository
from domain.order import Order, OrderStatus


class InMemoryOrderRepository(IOrderRepository):
    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}
        self._orders_counter: int = 0
        self._lock = threading.RLock()

    def get_by_id(self, order_id: UUID) -> Order | None:
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                return None
            return copy.deepcopy(order)

    def exists_by_id(self, order_id: UUID) -> bool:
        with self._lock:
            return order_id in self._orders

    def get_by_user_id(self, user_id: UUID) -> list[Order]:
        with self._lock:
            orders = [o for o in self._orders.values() if o.user_id == user_id]
            orders.sort(key=lambda o: o.created_at, reverse=True)
            return [copy.deepcopy(o) for o in orders]

    def list(
        self,
        filter_dto: OrderFilterDto | None = None,
    ) -> tuple[list[Order], int]:
        with self._lock:
            items = list(self._orders.values())

            if filter_dto is not None:
                paginated, total = filter_dto.apply(items)
            else:
                sorted_items = sorted(items, key=lambda o: o.created_at, reverse=True)
                total = len(sorted_items)
                paginated = sorted_items[:50]

            return [copy.deepcopy(o) for o in paginated], total

    def save(self, order: Order) -> Order:
        with self._lock:
            self._orders[order.id] = copy.deepcopy(order)
            return copy.deepcopy(order)

    def update_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        expected_status: OrderStatus | None = None,
    ) -> bool:
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                return False
            if expected_status is not None and order.status != expected_status:
                return False
            order.status = new_status
            return True

    def delete(self, order_id: UUID) -> bool:
        with self._lock:
            if order_id in self._orders:
                del self._orders[order_id]
                return True
            return False

    def increment_orders_count(self, amount: int = 1) -> int:
        with self._lock:
            self._orders_counter += amount
            return self._orders_counter

    def get_total_orders_count(self) -> int:
        with self._lock:
            return self._orders_counter
