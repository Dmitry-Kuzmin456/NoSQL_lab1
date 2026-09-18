from uuid import UUID

from application.cart.repository import ICartRepository
from domain.cart import Cart


class RiakCartRepository(ICartRepository):
    """Реализация репозитория корзины на базе Riak Map CRDT."""

    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        raise NotImplementedError

    def exists_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def has_product(self, user_id: UUID, product_id: UUID) -> bool:
        raise NotImplementedError

    def set_item_quantity(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> bool:
        raise NotImplementedError

    def add_or_update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
    ) -> bool:
        raise NotImplementedError

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        raise NotImplementedError

    def clear_cart(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def save(self, cart: Cart) -> Cart:
        raise NotImplementedError

    def delete_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError
