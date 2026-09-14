import copy
import threading
from uuid import UUID

from application.favourites.repository import IFavouritesRepository
from domain.favourites import Favourites


class InMemoryFavouritesRepository(IFavouritesRepository):
    def __init__(self) -> None:
        self._favourites: dict[UUID, Favourites] = {}
        self._lock = threading.RLock()

    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        with self._lock:
            fav = self._favourites.get(user_id)
            if fav is None:
                return None
            return copy.deepcopy(fav)

    def exists_by_user_id(self, user_id: UUID) -> bool:
        with self._lock:
            return user_id in self._favourites

    def is_favourite(self, user_id: UUID, product_id: UUID) -> bool:
        with self._lock:
            fav = self._favourites.get(user_id)
            if fav is None:
                return False
            return fav.has_product(product_id)

    def add_or_update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        added_user_id: UUID,
        note: str | None = None,
    ) -> bool:
        with self._lock:
            fav = self._favourites.get(user_id)
            if fav is None:
                fav = Favourites(user_id=user_id)
                self._favourites[user_id] = fav
            fav.add_product(
                product_id=product_id,
                added_user_id=added_user_id,
                note=note,
            )
            return True

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        with self._lock:
            fav = self._favourites.get(user_id)
            if fav is None or not fav.has_product(product_id):
                return False
            fav.remove_product(product_id)
            return True

    def clear_favourites(self, user_id: UUID) -> bool:
        with self._lock:
            fav = self._favourites.get(user_id)
            if fav is None:
                return False
            fav.clear()
            return True

    def save(self, favourites: Favourites) -> Favourites:
        with self._lock:
            self._favourites[favourites.user_id] = copy.deepcopy(favourites)
            return copy.deepcopy(favourites)

    def delete_by_user_id(self, user_id: UUID) -> bool:
        with self._lock:
            if user_id in self._favourites:
                del self._favourites[user_id]
                return True
            return False
