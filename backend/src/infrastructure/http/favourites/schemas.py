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
    note: str | None = Field(default=None, max_length=500, description="Заметка к товару в избранном")

    def to_dto(self) -> AddFavouriteDto:
        return AddFavouriteDto(
            product_id=self.product_id,
            note=self.note,
        )


class FavouriteItemResponse(BaseModel):
    product_id: UUID
    added_user_id: UUID
    updated_at: datetime
    note: str | None = None

    @classmethod
    def from_dto(cls, dto: FavouriteItemResponseDto) -> "FavouriteItemResponse":
        return cls(
            product_id=dto.product_id,
            added_user_id=dto.added_user_id,
            updated_at=dto.updated_at,
            note=dto.note,
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
