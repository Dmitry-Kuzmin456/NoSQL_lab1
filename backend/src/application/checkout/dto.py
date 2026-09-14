from dataclasses import dataclass
from decimal import Decimal

from application.order.dto import OrderResponseDto


@dataclass(frozen=True)
class CheckoutResultDto:
    orders: list[OrderResponseDto]
    total_orders: int
    total_amount: Decimal
