from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.order import Order, OrderStatus


@dataclass(frozen=True)
class CreateOrderDto:
    product_id: UUID
    quantity: int = 1


@dataclass(frozen=True)
class OrderFilterDto:
    user_id: UUID | None = None
    status: OrderStatus | None = None
    offset: int = 0
    limit: int = 50

    def matches(self, order: Order) -> bool:
        if self.user_id is not None and order.user_id != self.user_id:
            return False
        return not (self.status is not None and order.status != self.status)

    def apply(self, orders: list[Order]) -> tuple[list[Order], int]:
        sorted_orders = sorted(orders, key=lambda o: o.created_at, reverse=True)
        filtered = [o for o in sorted_orders if self.matches(o)]
        total = len(filtered)
        paginated = filtered[self.offset : self.offset + self.limit]
        return paginated, total


@dataclass(frozen=True)
class OrderResponseDto:
    id: UUID
    user_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime

    @classmethod
    def from_domain(cls, order: Order) -> "OrderResponseDto":
        return cls(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
        )


@dataclass(frozen=True)
class OrderListResponseDto:
    items: list[OrderResponseDto]
    total: int
    offset: int
    limit: int
