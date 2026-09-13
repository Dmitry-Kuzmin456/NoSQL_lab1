from abc import ABC, abstractmethod
from uuid import UUID

from domain.product import Product

from .dto import ProductFilterDto


class IProductRepository(ABC):
    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Product | None:
        """Получить товар по UUID."""
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        filter_dto: ProductFilterDto | None = None,
    ) -> tuple[list[Product], int]:
        """Получить список товаров с фильтрацией и пагинацией, а также общее количество."""
        raise NotImplementedError

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Сохранить или обновить товар."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        """Удалить товар по UUID."""
        raise NotImplementedError
