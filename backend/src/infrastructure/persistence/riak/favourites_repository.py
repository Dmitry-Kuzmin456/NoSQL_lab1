from datetime import UTC, datetime
from uuid import UUID

from application.favourites.repository import IFavouritesRepository
from domain.favourites import FavouriteProduct, Favourites
from infrastructure.persistence.riak.client import (
    RiakClient,
    get_riak_client,
)


class RiakFavouritesRepository(IFavouritesRepository):
    """Репозиторий избранного на основе Riak CRDT Map."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "favourites",
        bucket_type: str = "maps",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._bucket_type = bucket_type

    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        """Получить список избранного пользователя из CRDT карты."""
        data = self._client.map_get(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
        if not data or not isinstance(data, dict):
            return None

        products: list[FavouriteProduct] = []
        for key, val in data.items():
            if key.endswith("_map") and isinstance(val, dict):
                product_id_str = key[:-4]
                try:
                    product_id = UUID(product_id_str)
                    added_user_id_raw = val.get("added_user_id_register")
                    added_user_id = (
                        UUID(added_user_id_raw)
                        if isinstance(added_user_id_raw, str)
                        else user_id
                    )
                    updated_at_raw = val.get("updated_at_register")
                    updated_at = (
                        datetime.fromisoformat(updated_at_raw)
                        if isinstance(updated_at_raw, str)
                        else datetime.now(UTC)
                    )
                    products.append(
                        FavouriteProduct(
                            product_id=product_id,
                            added_user_id=added_user_id,
                            updated_at=updated_at,
                        )
                    )
                except (ValueError, TypeError):
                    continue

        return Favourites(user_id=user_id, products=products) if products else None

    def add_item(self, user_id: UUID, item: FavouriteProduct) -> bool:
        """Добавить товар в избранное через операцию обновления CRDT Map."""
        field_name = f"{item.product_id}_map"
        update_spec = {
            field_name: {
                "update": {
                    "added_user_id_register": str(item.added_user_id),
                    "updated_at_register": item.updated_at.isoformat(),
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
        """Удалить товар из избранного через операцию remove поля CRDT Map."""
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
        """Удалить CRDT карту избранного пользователя."""
        return self._client.delete(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
