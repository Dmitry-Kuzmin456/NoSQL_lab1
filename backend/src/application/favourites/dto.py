from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.favourites import FavouriteProduct, Favourites


@dataclass(frozen=True)
class AddFavouriteDto:
    product_id: UUID


@dataclass(frozen=True)
class FavouriteItemResponseDto:
    product_id: UUID
    added_user_id: UUID
    updated_at: datetime

    @classmethod
    def from_domain(cls, item: FavouriteProduct) -> "FavouriteItemResponseDto":
        return cls(
            product_id=item.product_id,
            added_user_id=item.added_user_id,
            updated_at=item.updated_at,
        )


@dataclass(frozen=True)
class FavouritesResponseDto:
    user_id: UUID
    products: list[FavouriteItemResponseDto]
    total_count: int

    @classmethod
    def from_domain(cls, favourites: Favourites) -> "FavouritesResponseDto":
        items = [FavouriteItemResponseDto.from_domain(p) for p in favourites.products]
        return cls(
            user_id=favourites.user_id,
            products=items,
            total_count=len(items),
        )
