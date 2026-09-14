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

    def exists_by_user_id(self, user_id: UUID) -> bool:
        with self._lock:
            return user_id in self._carts

    def has_product(self, user_id: UUID, product_id: UUID) -> bool:
        with self._lock:
            cart = self._carts.get(user_id)
            if cart is None:
                return False
            return cart.has_product(product_id)

    def add_or_update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> bool:
        with self._lock:
            cart = self._carts.get(user_id)
            if cart is None:
                cart = Cart(user_id=user_id)
                self._carts[user_id] = cart
            cart.update_quantity(product_id, quantity)
            return True

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        with self._lock:
            cart = self._carts.get(user_id)
            if cart is None or not cart.has_product(product_id):
                return False
            cart.remove_product(product_id)
            return True

    def clear_cart(self, user_id: UUID) -> bool:
        with self._lock:
            cart = self._carts.get(user_id)
            if cart is None:
                return False
            cart.clear()
            return True

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
