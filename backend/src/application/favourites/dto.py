from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.product.dto import ProductResponseDto
from domain.favourites import FavouriteProduct, Favourites


@dataclass(frozen=True)
class AddFavouriteDto:
    product_id: UUID


@dataclass(frozen=True)
class FavouriteItemResponseDto:
    product_id: UUID
    added_user_id: UUID
    updated_at: datetime
    product: ProductResponseDto | None = None
    is_available: bool = True

    @classmethod
    def from_domain(
        cls,
        item: FavouriteProduct,
        product: ProductResponseDto | None = None,
        is_available: bool = True,
    ) -> "FavouriteItemResponseDto":
        return cls(
            product_id=item.product_id,
            added_user_id=item.added_user_id,
            updated_at=item.updated_at,
            product=product,
            is_available=is_available,
        )


@dataclass(frozen=True)
class FavouritesResponseDto:
    user_id: UUID
    products: list[FavouriteItemResponseDto]
    total_count: int

    @classmethod
    def from_domain(
        cls,
        favourites: Favourites,
        products: list[FavouriteItemResponseDto] | None = None,
    ) -> "FavouritesResponseDto":
        if products is None:
            products = [
                FavouriteItemResponseDto.from_domain(p) for p in favourites.products
            ]
        return cls(
            user_id=favourites.user_id,
            products=products,
            total_count=len(products),
        )
