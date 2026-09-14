from abc import ABC, abstractmethod
from uuid import UUID

from domain.cart import Cart


class ICartRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя по user_id."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Проверить существование корзины пользователя без вычитки элементов."""
        raise NotImplementedError

    @abstractmethod
    def has_product(self, user_id: UUID, product_id: UUID) -> bool:
        """Проверить наличие конкретного товара в корзине пользователя без загрузки всей корзины."""
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
        """Удалить конкретный товар из корзины без загрузки всей корзины."""
        raise NotImplementedError

    @abstractmethod
    def clear_cart(self, user_id: UUID) -> bool:
        """Очистить все товары из корзины пользователя."""
        raise NotImplementedError

    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Сохранить или обновить корзину целиком."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить корзину пользователя."""
        raise NotImplementedError
