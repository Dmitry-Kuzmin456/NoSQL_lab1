from typing import Annotated

from fastapi import Depends

from application.checkout.service import CheckoutService
from infrastructure.event_bus.dependencies import EventBusDep
from infrastructure.http.cart.dependencies import CartServiceDep
from infrastructure.http.order.dependencies import OrderServiceDep


def get_checkout_service(
    cart_service: CartServiceDep,
    order_service: OrderServiceDep,
    event_bus: EventBusDep,
) -> CheckoutService:
    return CheckoutService(
        cart_service=cart_service,
        order_service=order_service,
        event_bus=event_bus,
    )


CheckoutServiceDep = Annotated[CheckoutService, Depends(get_checkout_service)]
