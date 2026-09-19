from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from application.cart.dto import (
    CartItemResponseDto,
    CartResponseDto,
    UpdateCartProductDto,
)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(
        ...,
        ge=0,
        description="Новое количество товара (если 0 — товар будет удален)",
    )

    def to_dto(self, product_id: UUID) -> UpdateCartProductDto:
        return UpdateCartProductDto(
            product_id=product_id,
            quantity=self.quantity,
        )


class CartItemResponse(BaseModel):
    product_id: UUID
    quantity: int
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: CartItemResponseDto) -> "CartItemResponse":
        return cls(
            product_id=dto.product_id,
            quantity=dto.quantity,
            updated_at=dto.updated_at,
        )


class CartResponse(BaseModel):
    user_id: UUID
    items: list[CartItemResponse]
    total_items: int

    @classmethod
    def from_dto(cls, dto: CartResponseDto) -> "CartResponse":
        return cls(
            user_id=dto.user_id,
            items=[CartItemResponse.from_dto(item) for item in dto.items],
            total_items=dto.total_items,
        )
