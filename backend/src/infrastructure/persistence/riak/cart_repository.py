from datetime import UTC, datetime
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

    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Получить корзину пользователя из CRDT карты."""
        data = self._client.map_get(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
        if not data or not isinstance(data, dict):
            return None

        cart_products: list[CartProduct] = []
        for key, val in data.items():
            if key.endswith("_map") and isinstance(val, dict):
                product_id_str = key[:-4]
                try:
                    product_id = UUID(product_id_str)
                    qty_raw = val.get("quantity_register")
                    quantity = int(qty_raw) if isinstance(qty_raw, str | int) else 1
                    updated_at_raw = val.get("updated_at_register")
                    updated_at = (
                        datetime.fromisoformat(updated_at_raw)
                        if isinstance(updated_at_raw, str)
                        else datetime.now(UTC)
                    )
                    cart_products.append(
                        CartProduct(
                            product_id=product_id,
                            quantity=quantity,
                            updated_at=updated_at,
                        )
                    )
                except (ValueError, TypeError):
                    continue

        return (
            Cart(user_id=user_id, cart_products=cart_products)
            if cart_products
            else None
        )

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
        )
        return True

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из CRDT карты корзины."""
        field_name = f"{product_id}_map"
        update_spec = {field_name: "remove"}
        self._client.map_update(
            bucket=self._bucket,
            key=str(user_id),
            update_spec=update_spec,
            bucket_type=self._bucket_type,
        )
        return True

    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить CRDT карту корзины пользователя."""
        return self._client.delete(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
