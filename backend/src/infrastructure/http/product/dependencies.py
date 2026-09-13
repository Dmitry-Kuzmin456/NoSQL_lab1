from typing import Annotated

from fastapi import Depends

from application.product.repository import IProductRepository
from application.product.service import ProductService
from infrastructure.persistence.in_memory.product_repository import (
    InMemoryProductRepository,
)

_product_repository: IProductRepository = InMemoryProductRepository()


def get_product_repository() -> IProductRepository:
    return _product_repository


ProductRepositoryDep = Annotated[IProductRepository, Depends(get_product_repository)]


def get_product_service(
    product_repository: ProductRepositoryDep,
) -> ProductService:
    return ProductService(product_repository=product_repository)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
