from datetime import datetime
from typing import Any
from uuid import UUID

from application.cart.repository import ICartRepository
from domain.cart import Cart, CartProduct
from infrastructure.persistence.riak.client import (
    RiakClient,
    RiakObject,
    get_riak_client,
)


class RiakCartRepository(ICartRepository):
    """Репозиторий корзины для Riak KV."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "carts",
        bucket_type: str = "default",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._bucket_type = bucket_type

    @staticmethod
    def _cart_to_dict(cart: Cart) -> dict[str, Any]:
        return {
            "user_id": str(cart.user_id),
            "cart_products": [
                {
                    "product_id": str(p.product_id),
                    "quantity": p.quantity,
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in cart.cart_products
            ],
        }

    @staticmethod
    def _dict_to_cart(data: dict[str, Any]) -> Cart:
        cart_products = [
            CartProduct(
                product_id=UUID(item["product_id"]),
                quantity=item["quantity"],
                updated_at=datetime.fromisoformat(item["updated_at"]),
            )
            for item in data.get("cart_products", [])
        ]
        return Cart(
            user_id=UUID(data["user_id"]),
            cart_products=cart_products,
        )

    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя."""
        obj = self._client.get(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
        if obj is None or not isinstance(obj.data, dict):
            return None
        return self._dict_to_cart(obj.data)

    def save(self, cart: Cart) -> Cart:
        """Сохранить корзину."""
        obj = RiakObject(
            bucket=self._bucket,
            key=str(cart.user_id),
            data=self._cart_to_dict(cart),
            bucket_type=self._bucket_type,
            vclock=None,
        )
        self._client.put(obj)
        return cart

    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить корзину пользователя."""
        return self._client.delete(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
