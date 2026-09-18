from abc import ABC, abstractmethod
from uuid import UUID

from domain.cart import Cart


class ICartRepository(ABC):
    """Интерфейс корзины покупателя на базе Riak Map CRDT."""

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя по ключу user_id (O(1))."""
        raise NotImplementedError

    @abstractmethod
    def has_product(self, user_id: UUID, product_id: UUID) -> bool:
        """Проверить наличие конкретного товара в корзине пользователя."""
        raise NotImplementedError

    @abstractmethod
    def set_item_quantity(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> bool:
        """Обновить количество товара внутри Map CRDT без перезаписи всей корзины."""
        raise NotImplementedError

    @abstractmethod
    def add_or_update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> bool:
        """Добавить товар в корзину или изменить его количество без загрузки всей корзины."""
        raise NotImplementedError

    @abstractmethod
    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить позицию из корзины (CRDT Map field remove)."""
        raise NotImplementedError

    @abstractmethod
    def clear_cart(self, user_id: UUID) -> bool:
        """Очистить корзину пользователя (DELETE /carts/{user_id})."""
        raise NotImplementedError

    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Сохранить или обновить корзину целиком."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить корзину пользователя."""
        raise NotImplementedError
