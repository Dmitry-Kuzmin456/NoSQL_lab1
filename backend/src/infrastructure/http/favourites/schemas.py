from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from application.favourites.dto import (
    AddFavouriteDto,
    FavouriteItemResponseDto,
    FavouritesResponseDto,
)


class AddFavouriteRequest(BaseModel):
    product_id: UUID = Field(..., description="ID добавляемого товара")

    def to_dto(self) -> AddFavouriteDto:
        return AddFavouriteDto(
            product_id=self.product_id,
        )


class FavouriteItemResponse(BaseModel):
    product_id: UUID
    added_user_id: UUID
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: FavouriteItemResponseDto) -> "FavouriteItemResponse":
        return cls(
            product_id=dto.product_id,
            added_user_id=dto.added_user_id,
            updated_at=dto.updated_at,
        )


class FavouritesResponse(BaseModel):
    user_id: UUID
    products: list[FavouriteItemResponse]
    total_count: int

    @classmethod
    def from_dto(cls, dto: FavouritesResponseDto) -> "FavouritesResponse":
        return cls(
            user_id=dto.user_id,
            products=[FavouriteItemResponse.from_dto(p) for p in dto.products],
            total_count=dto.total_count,
        )
