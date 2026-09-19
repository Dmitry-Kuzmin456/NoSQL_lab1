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
    def add_item(self, user_id: UUID, item: FavouriteProduct) -> bool:
        """Добавить товар в избранное."""
        raise NotImplementedError

    @abstractmethod
    def add_item_and_get(self, user_id: UUID, item: FavouriteProduct) -> Favourites:
        """Добавить товар в избранное и вернуть обновленный список в одном запросе."""
        raise NotImplementedError

    @abstractmethod
    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из избранного."""
        raise NotImplementedError

    @abstractmethod
    def remove_item_and_get(self, user_id: UUID, product_id: UUID) -> Favourites:
        """Удалить товар из избранного и вернуть обновленный список в одном запросе."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить список избранного пользователя."""
        raise NotImplementedError
