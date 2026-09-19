from datetime import datetime
from typing import Any
from uuid import UUID

from application.favourites.repository import IFavouritesRepository
from domain.favourites import FavouriteProduct, Favourites
from infrastructure.persistence.riak.client import (
    RiakClient,
    RiakObject,
    get_riak_client,
)


class RiakFavouritesRepository(IFavouritesRepository):
    """Репозиторий избранного для Riak KV."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "favourites",
        bucket_type: str = "default",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._bucket_type = bucket_type

    @staticmethod
    def _favourites_to_dict(favourites: Favourites) -> dict[str, Any]:
        return {
            "user_id": str(favourites.user_id),
            "products": [
                {
                    "product_id": str(p.product_id),
                    "added_user_id": str(p.added_user_id),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in favourites.products
            ],
        }

    @staticmethod
    def _dict_to_favourites(data: dict[str, Any]) -> Favourites:
        products = [
            FavouriteProduct(
                product_id=UUID(item["product_id"]),
                added_user_id=UUID(item["added_user_id"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
            )
            for item in data.get("products", [])
        ]
        return Favourites(
            user_id=UUID(data["user_id"]),
            products=products,
        )

    def get_by_user_id(self, user_id: UUID) -> Favourites | None:
        """Получить список избранного пользователя."""
        obj = self._client.get(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
        if obj is None or not isinstance(obj.data, dict):
            return None
        return self._dict_to_favourites(obj.data)

    def add_item(self, user_id: UUID, item: FavouriteProduct) -> bool:
        """Добавить товар в избранное."""
        favourites = self.get_by_user_id(user_id)
        if favourites is None:
            favourites = Favourites(user_id=user_id, products=[])

        for existing in favourites.products:
            if existing.product_id == item.product_id:
                return False

        favourites.products.append(item)
        self.save(favourites)
        return True

    def remove_item(self, user_id: UUID, product_id: UUID) -> bool:
        """Удалить товар из избранного."""
        favourites = self.get_by_user_id(user_id)
        if favourites is None:
            return False

        initial_len = len(favourites.products)
        favourites.products = [
            p for p in favourites.products if p.product_id != product_id
        ]
        if len(favourites.products) == initial_len:
            return False

        self.save(favourites)
        return True

    def clear(self, user_id: UUID) -> bool:
        """Очистить список избранного пользователя."""
        favourites = self.get_by_user_id(user_id)
        if favourites is None:
            return False
        favourites.products.clear()
        self.save(favourites)
        return True

    def save(self, favourites: Favourites) -> Favourites:
        """Сохранить список избранного."""
        obj = RiakObject(
            bucket=self._bucket,
            key=str(favourites.user_id),
            data=self._favourites_to_dict(favourites),
            bucket_type=self._bucket_type,
            vclock=None,
        )
        self._client.put(obj)
        return favourites
