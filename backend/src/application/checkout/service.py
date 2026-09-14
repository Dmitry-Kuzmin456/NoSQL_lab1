from decimal import Decimal
from uuid import UUID

from application.cart.service import CartService
from application.order.dto import CreateOrderDto, OrderResponseDto
from application.order.service import OrderService

from .dto import CheckoutResultDto
from .exceptions import EmptyCartCheckoutException


class CheckoutService:
    def __init__(
        self,
        cart_service: CartService,
        order_service: OrderService,
    ) -> None:
        self._cart_service = cart_service
        self._order_service = order_service

    def checkout(self, user_id: UUID) -> CheckoutResultDto:
        cart_dto = self._cart_service.get_by_user_id(user_id)
        if not cart_dto.items:
            raise EmptyCartCheckoutException()

        created_orders: list[OrderResponseDto] = []
        for item in cart_dto.items:
            order_dto = self._order_service.create(
                user_id=user_id,
                dto=CreateOrderDto(
                    product_id=item.product_id,
                    quantity=item.quantity,
                ),
            )
            created_orders.append(order_dto)

        self._cart_service.clear(user_id)

        total_amount = sum(
            (order.total_amount for order in created_orders),
            start=Decimal("0.00"),
        )

        return CheckoutResultDto(
            orders=created_orders,
            total_orders=len(created_orders),
            total_amount=total_amount,
        )
