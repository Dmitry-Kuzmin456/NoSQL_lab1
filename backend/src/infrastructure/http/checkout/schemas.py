from decimal import Decimal

from pydantic import BaseModel

from application.checkout.dto import CheckoutResultDto
from infrastructure.http.order.schemas import OrderResponse


class CheckoutResponse(BaseModel):
    orders: list[OrderResponse]
    total_orders: int
    total_amount: Decimal

    @classmethod
    def from_dto(cls, dto: CheckoutResultDto) -> "CheckoutResponse":
        return cls(
            orders=[OrderResponse.from_dto(o) for o in dto.orders],
            total_orders=dto.total_orders,
            total_amount=dto.total_amount,
        )
