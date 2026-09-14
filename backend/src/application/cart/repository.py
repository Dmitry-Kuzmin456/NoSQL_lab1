from abc import ABC, abstractmethod
from uuid import UUID

from domain.cart import Cart


class ICartRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя по user_id."""
        raise NotImplementedError

    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Сохранить или обновить корзину."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить корзину пользователя."""
        raise NotImplementedError
