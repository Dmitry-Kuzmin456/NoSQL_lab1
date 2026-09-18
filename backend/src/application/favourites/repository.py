from abc import ABC, abstractmethod
from uuid import UUID

from domain.favourites import FavouriteProduct, Favourites


class IFavouritesRepository(ABC):
    """Интерфейс репозитория избранного на базе Riak OR-Set / Map CRDT."""

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        """Точечное чтение O(1) списка избранного по ключу user_id."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Быстрая проверка существования ключа через HEAD-запрос (без передачи payload)."""
        raise NotImplementedError

    @abstractmethod
    def is_favourite(self, user_id: UUID, product_id: UUID) -> bool:
        """Проверить наличие элемента в множестве без десериализации всего списка."""
        raise NotImplementedError

    @abstractmethod
    def add_item(self, user_id: UUID, item: FavouriteProduct) -> bool:
        """CRDT-мутация добавления элемента в OR-Set без полного чтения всего списка."""
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
        """CRDT-мутация удаления элемента из OR-Set без предварительной выгрузки."""
        raise NotImplementedError

    @abstractmethod
    def clear(self, user_id: UUID) -> bool:
        """Удаление ключа user_id (DELETE /favourites/{user_id})."""
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
