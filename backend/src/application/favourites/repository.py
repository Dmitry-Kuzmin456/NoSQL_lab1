from abc import ABC, abstractmethod
from uuid import UUID

from domain.favourites import FavouriteProduct, Favourites


class IFavouritesRepository(ABC):
    """Интерфейс репозитория избранного."""

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        """Получить список избранного пользователя."""
        raise NotImplementedError

    @abstractmethod
    def add_or_update_item(self, user_id: UUID, item: FavouriteProduct) -> bool:
        """Добавить или обновить товар в избранном."""
        raise NotImplementedError

    @abstractmethod
    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из избранного."""
        raise NotImplementedError

    @abstractmethod
    def clear(self, user_id: UUID) -> bool:
        """Очистить список избранного пользователя."""
        raise NotImplementedError

    @abstractmethod
    def save(self, favourites: Favourites) -> Favourites:
        """Сохранить список избранного."""
        raise NotImplementedError
