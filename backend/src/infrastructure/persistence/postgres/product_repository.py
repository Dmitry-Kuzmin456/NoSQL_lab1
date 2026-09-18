from uuid import UUID

from application.product.dto import ProductFilterDto
from application.product.repository import IProductRepository
from domain.product import Product


class PostgresProductRepository(IProductRepository):
    """Реализация репозитория товаров для PostgreSQL."""

    def get_by_id(self, product_id: UUID) -> Product | None:
        raise NotImplementedError

    def exists_by_id(self, product_id: UUID) -> bool:
        raise NotImplementedError

    def list(
        self,
        filter_dto: ProductFilterDto | None = None,
    ) -> tuple[list[Product], int]:
        raise NotImplementedError

    def save(self, product: Product) -> Product:
        raise NotImplementedError

    def update_stock(self, product_id: UUID, delta: int) -> bool:
        raise NotImplementedError

    def delete(self, product_id: UUID) -> bool:
        raise NotImplementedError
