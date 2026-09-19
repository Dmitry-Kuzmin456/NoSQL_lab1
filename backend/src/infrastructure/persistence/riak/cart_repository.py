from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from application.cart.repository import ICartRepository
from domain.cart import Cart, CartProduct
from infrastructure.persistence.riak.client import (
    RiakClient,
    get_riak_client,
)


class RiakCartRepository(ICartRepository):
    """Репозиторий корзины на основе Riak CRDT Map."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "carts",
        bucket_type: str = "maps",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._bucket_type = bucket_type

    def _data_to_cart(self, user_id: UUID, data: dict[str, Any] | None) -> Cart | None:
        if not isinstance(data, dict):
            return None

        cart_products = [
            item
            for key, val in data.items()
            if (item := self._parse_cart_product(key, val)) is not None
        ]
        return (
            Cart(user_id=user_id, cart_products=cart_products)
            if cart_products
            else None
        )

    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя из CRDT карты."""
        data = self._client.map_get(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
        return self._data_to_cart(user_id, data)

    @staticmethod
    def _parse_updated_at(raw: Any) -> datetime:
        if isinstance(raw, str):
            try:
                return datetime.fromisoformat(raw)
            except ValueError:
                pass
        return datetime.now(UTC)

    @classmethod
    def _parse_cart_product(cls, key: str, val: Any) -> CartProduct | None:
        if not key.endswith("_map") or not isinstance(val, dict):
            return None
        try:
            product_id = UUID(key[:-4])
            qty_raw = val.get("quantity_register")
            quantity = int(qty_raw) if isinstance(qty_raw, str | int) else 1
            updated_at = cls._parse_updated_at(val.get("updated_at_register"))
            return CartProduct(
                product_id=product_id,
                quantity=quantity,
                updated_at=updated_at,
            )
        except (ValueError, TypeError):
            return None

    def set_item_quantity(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
        updated_at: datetime | None = None,
    ) -> bool:
        """Установить количество товара в CRDT карте корзины."""
        dt = updated_at or datetime.now(UTC)
        field_name = f"{product_id}_map"
        update_spec = {
            field_name: {
                "update": {
                    "quantity_register": str(quantity),
                    "updated_at_register": dt.isoformat(),
                }
            }
        }
        self._client.map_update(
            bucket=self._bucket,
            key=str(user_id),
            update_spec=update_spec,
            bucket_type=self._bucket_type,
            return_body=False,
        )
        return True

    def set_item_quantity_and_get(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int,
        updated_at: datetime | None = None,
    ) -> Cart:
        """Установить количество товара в CRDT карте корзины и вернуть обновленную корзину."""
        dt = updated_at or datetime.now(UTC)
        field_name = f"{product_id}_map"
        update_spec = {
            field_name: {
                "update": {
                    "quantity_register": str(quantity),
                    "updated_at_register": dt.isoformat(),
                }
            }
        }
        data = self._client.map_update(
            bucket=self._bucket,
            key=str(user_id),
            update_spec=update_spec,
            bucket_type=self._bucket_type,
            return_body=True,
        )
        cart = self._data_to_cart(user_id, data)
        return cart if cart is not None else Cart(user_id=user_id)

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из CRDT карты корзины."""
        field_name = f"{product_id}_map"
        update_spec = {field_name: "remove"}
        self._client.map_update(
            bucket=self._bucket,
            key=str(user_id),
            update_spec=update_spec,
            bucket_type=self._bucket_type,
            return_body=False,
        )
        return True

    def remove_item_and_get(self, user_id: UUID, product_id: UUID) -> Cart:
        """Удалить товар из CRDT карты корзины и вернуть обновленную корзину."""
        field_name = f"{product_id}_map"
        update_spec = {field_name: "remove"}
        data = self._client.map_update(
            bucket=self._bucket,
            key=str(user_id),
            update_spec=update_spec,
            bucket_type=self._bucket_type,
            return_body=True,
        )
        cart = self._data_to_cart(user_id, data)
        return cart if cart is not None else Cart(user_id=user_id)

    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить CRDT карту корзины пользователя."""
        return self._client.delete(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
