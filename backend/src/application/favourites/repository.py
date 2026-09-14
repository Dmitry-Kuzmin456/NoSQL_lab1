from abc import ABC, abstractmethod
from uuid import UUID

from domain.favourites import Favourites


class IFavouritesRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        """Получить список избранного пользователя по user_id."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Проверить существование списка избранного пользователя."""
        raise NotImplementedError

    @abstractmethod
    def is_favourite(self, user_id: UUID, product_id: UUID) -> bool:
        """Проверить, находится ли товар в избранном пользователя без загрузки полного списка."""
        raise NotImplementedError

    @abstractmethod
    def add_or_update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        added_user_id: UUID,
        note: str | None = None,
    ) -> bool:
        """Добавить или обновить товар в избранном без предварительной загрузки всего списка."""
        raise NotImplementedError

    @abstractmethod
    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из избранного пользователя без загрузки всего списка."""
        raise NotImplementedError

    @abstractmethod
    def clear_favourites(self, user_id: UUID) -> bool:
        """Очистить все товары из избранного пользователя."""
        raise NotImplementedError

    @abstractmethod
    def save(self, favourites: Favourites) -> Favourites:
        """Сохранить или обновить список избранного целиком."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить избранное пользователя."""
        raise NotImplementedError
