from typing import Annotated

from fastapi import Depends

from application.order.repository import IOrderRepository
from application.order.service import OrderService
from infrastructure.http.product.dependencies import ProductServiceDep
from infrastructure.persistence.in_memory.order_repository import (
    InMemoryOrderRepository,
)

_order_repository: IOrderRepository = InMemoryOrderRepository()


def get_order_repository() -> IOrderRepository:
    return _order_repository


OrderRepositoryDep = Annotated[IOrderRepository, Depends(get_order_repository)]


def get_order_service(
    order_repository: OrderRepositoryDep,
    product_service: ProductServiceDep,
) -> OrderService:
    return OrderService(
        order_repository=order_repository,
        product_service=product_service,
    )


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
