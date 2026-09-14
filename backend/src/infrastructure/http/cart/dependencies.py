from typing import Annotated

from fastapi import Depends

from application.cart.repository import ICartRepository
from application.cart.service import CartService
from infrastructure.http.product.dependencies import ProductServiceDep
from infrastructure.persistence.in_memory.cart_repository import (
    InMemoryCartRepository,
)

_cart_repository: ICartRepository = InMemoryCartRepository()


def get_cart_repository() -> ICartRepository:
    return _cart_repository


CartRepositoryDep = Annotated[ICartRepository, Depends(get_cart_repository)]


def get_cart_service(
    cart_repository: CartRepositoryDep,
    product_service: ProductServiceDep,
) -> CartService:
    return CartService(
        cart_repository=cart_repository,
        product_service=product_service,
    )


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]
