from decimal import Decimal
from uuid import UUID

from application.cart.service import CartService
from application.event_bus import IEventBus
from application.order.dto import CreateOrderDto, OrderResponseDto
from application.order.service import OrderService
from domain.history import OperationEvent, OperationType

from .dto import CheckoutResultDto
from .exceptions import EmptyCartCheckoutException


class CheckoutService:
    def __init__(
        self,
        cart_service: CartService,
        order_service: OrderService,
        event_bus: IEventBus,
    ) -> None:
        self._cart_service = cart_service
        self._order_service = order_service
        self._event_bus = event_bus

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

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.CHECKOUT,
                details={
                    "total_orders": len(created_orders),
                    "total_amount": f"{total_amount:.2f}",
                },
            )
        )

        return CheckoutResultDto(
            orders=created_orders,
            total_orders=len(created_orders),
            total_amount=total_amount,
        )
