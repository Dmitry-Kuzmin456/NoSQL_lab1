from uuid import UUID

from application.favourites.repository import IFavouritesRepository
from domain.favourites import FavouriteProduct, Favourites


class RiakFavouritesRepository(IFavouritesRepository):
    """Реализация репозитория избранного на базе Riak OR-Set / Map CRDT."""

    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        raise NotImplementedError

    def exists_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def is_favourite(self, user_id: UUID, product_id: UUID) -> bool:
        raise NotImplementedError

    def add_item(self, user_id: UUID, item: FavouriteProduct) -> bool:
        raise NotImplementedError

    def add_or_update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        added_user_id: UUID,
        note: str | None = None,
    ) -> bool:
        raise NotImplementedError

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        raise NotImplementedError

    def clear(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def clear_favourites(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def save(self, favourites: Favourites) -> Favourites:
        raise NotImplementedError

    def delete_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError
