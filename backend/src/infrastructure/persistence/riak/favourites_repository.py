from uuid import UUID

from application.favourites.repository import IFavouritesRepository
from domain.favourites import FavouriteProduct, Favourites


class RiakFavouritesRepository(IFavouritesRepository):
    """Репозиторий избранного для Riak KV."""

    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        raise NotImplementedError

    def is_favourite(self, user_id: UUID, product_id: UUID) -> bool:
        raise NotImplementedError

    def add_or_update_item(self, user_id: UUID, item: FavouriteProduct) -> bool:
        raise NotImplementedError

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        raise NotImplementedError

    def clear(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def save(self, favourites: Favourites) -> Favourites:
        raise NotImplementedError
