from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from application.cart.dto import (
    CartItemResponseDto,
    CartResponseDto,
    UpdateCartProductDto,
)
from infrastructure.http.product.schemas import ProductResponse


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
    product: ProductResponse | None = None
    subtotal: Decimal = Field(
        default=Decimal("0.00"), description="Подытог по позиции (цена * кол-во)"
    )
    is_available: bool = Field(
        default=True,
        description="Доступен ли товар на складе в запрашиваемом количестве",
    )
    available_stock: int = Field(default=0, description="Текущий остаток на складе")

    @classmethod
    def from_dto(cls, dto: CartItemResponseDto) -> "CartItemResponse":
        return cls(
            product_id=dto.product_id,
            quantity=dto.quantity,
            updated_at=dto.updated_at,
            product=ProductResponse.from_dto(dto.product) if dto.product else None,
            subtotal=dto.subtotal,
            is_available=dto.is_available,
            available_stock=dto.available_stock,
        )


class CartResponse(BaseModel):
    user_id: UUID
    items: list[CartItemResponse]
    total_items: int
    total_amount: Decimal = Field(
        default=Decimal("0.00"), description="Общая стоимость товаров в корзине"
    )
    has_unavailable_items: bool = Field(
        default=False, description="Есть ли в корзине недоступные товары"
    )

    @classmethod
    def from_dto(cls, dto: CartResponseDto) -> "CartResponse":
        return cls(
            user_id=dto.user_id,
            items=[CartItemResponse.from_dto(item) for item in dto.items],
            total_items=dto.total_items,
            total_amount=dto.total_amount,
            has_unavailable_items=dto.has_unavailable_items,
        )
