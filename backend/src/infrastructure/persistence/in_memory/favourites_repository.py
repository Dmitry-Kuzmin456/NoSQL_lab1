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
