from abc import ABC, abstractmethod
from uuid import UUID

from domain.cart import Cart


class ICartRepository(ABC):
    """Интерфейс репозитория корзины."""

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя."""
        pass

    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Сохранить корзину."""
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить корзину пользователя."""
        pass
