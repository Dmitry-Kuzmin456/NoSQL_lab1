import copy
import threading
from uuid import UUID

from application.cart.repository import ICartRepository
from domain.cart import Cart


class InMemoryCartRepository(ICartRepository):
    def __init__(self) -> None:
        self._carts: dict[UUID, Cart] = {}
        self._lock = threading.RLock()

    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        with self._lock:
            cart = self._carts.get(user_id)
            if cart is None:
                return None
            return copy.deepcopy(cart)

    def save(self, cart: Cart) -> Cart:
        with self._lock:
            self._carts[cart.user_id] = copy.deepcopy(cart)
            return copy.deepcopy(cart)

    def delete_by_user_id(self, user_id: UUID) -> bool:
        with self._lock:
            if user_id in self._carts:
                del self._carts[user_id]
                return True
            return False
