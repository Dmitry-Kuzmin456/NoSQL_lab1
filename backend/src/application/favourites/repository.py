from abc import ABC, abstractmethod
from uuid import UUID

from domain.favourites import Favourites


class IFavouritesRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        """Получить список избранного пользователя по user_id."""
        raise NotImplementedError

    @abstractmethod
    def save(self, favourites: Favourites) -> Favourites:
        """Сохранить или обновить список избранного."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить избранное пользователя."""
        raise NotImplementedError
