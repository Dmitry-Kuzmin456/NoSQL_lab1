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
    def exists_by_id(self, product_id: UUID) -> bool:
        """Проверить существование товара по UUID без загрузки данных объекта."""
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
    def update_stock(self, product_id: UUID, delta: int) -> bool:
        """Изменить остаток товара на складе на величину delta."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        """Удалить товар по UUID."""
        raise NotImplementedError
