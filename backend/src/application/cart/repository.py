from abc import ABC, abstractmethod
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
    ) -> bool:
        """Установить количество товара в корзине."""
        raise NotImplementedError

    @abstractmethod
    def add_or_update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> bool:
        """Добавить товар в корзину или обновить его количество."""
        raise NotImplementedError

    @abstractmethod
    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из корзины."""
        raise NotImplementedError

    @abstractmethod
    def clear_cart(self, user_id: UUID) -> bool:
        """Очистить корзину пользователя."""
        raise NotImplementedError

    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Сохранить корзину."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить корзину пользователя."""
        raise NotImplementedError
