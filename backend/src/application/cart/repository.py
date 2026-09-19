from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from domain.cart import Cart


class ICartRepository(ABC):
    """Интерфейс репозитория корзины."""

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя."""
        raise NotImplementedError

    @abstractmethod
    def set_item_quantity(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
        updated_at: datetime | None = None,
    ) -> bool:
        """Установить количество товара в корзине."""
        raise NotImplementedError

    @abstractmethod
    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из корзины."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить корзину пользователя."""
        raise NotImplementedError
