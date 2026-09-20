from abc import ABC, abstractmethod
from uuid import UUID

from domain.product import Product

from .dto import ProductFilterDto


class IProductRepository(ABC):
    """Интерфейс репозитория товаров."""

    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Product | None:
        """Получить товар по ID."""
        raise NotImplementedError

    @abstractmethod
    def get_by_ids(self, product_ids: list[UUID]) -> list[Product]:
        """Получить список товаров по их ID."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, product_id: UUID) -> bool:
        """Проверить существование товара."""
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        filter_dto: ProductFilterDto | None = None,
    ) -> list[Product]:
        """Получить список товаров с фильтрацией."""
        raise NotImplementedError

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Сохранить товар."""
        raise NotImplementedError

    @abstractmethod
    def update_stock(self, product_id: UUID, delta: int) -> bool:
        """Изменить остаток товара на складе."""
        raise NotImplementedError

    @abstractmethod
    def update_stock_and_get(self, product_id: UUID, delta: int) -> Product | None:
        """Изменить остаток товара на складе и вернуть обновленный товар в одном запросе."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        """Удалить товар."""
        raise NotImplementedError
