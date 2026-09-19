from datetime import UTC, datetime
from typing import Any
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
        if not isinstance(data, dict):
            return None

        products = [
            item
            for key, val in data.items()
            if (item := self._parse_favourite_product(key, val, user_id)) is not None
        ]
        return Favourites(user_id=user_id, products=products) if products else None

    @staticmethod
    def _parse_updated_at(raw: Any) -> datetime:
        if isinstance(raw, str):
            try:
                return datetime.fromisoformat(raw)
            except ValueError:
                pass
        return datetime.now(UTC)

    @classmethod
    def _parse_favourite_product(
        cls,
        key: str,
        val: Any,
        default_user_id: UUID,
    ) -> FavouriteProduct | None:
        if not key.endswith("_map") or not isinstance(val, dict):
            return None
        try:
            product_id = UUID(key[:-4])
            added_user_id_raw = val.get("added_user_id_register")
            added_user_id = (
                UUID(added_user_id_raw)
                if isinstance(added_user_id_raw, str)
                else default_user_id
            )
            updated_at = cls._parse_updated_at(val.get("updated_at_register"))
            return FavouriteProduct(
                product_id=product_id,
                added_user_id=added_user_id,
                updated_at=updated_at,
            )
        except (ValueError, TypeError):
            return None

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
