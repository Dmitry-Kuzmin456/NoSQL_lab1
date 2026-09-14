from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from application.order.dto import (
    CreateOrderDto,
    OrderFilterDto,
    OrderListResponseDto,
    OrderResponseDto,
)
from domain.order import OrderStatus


class CreateOrderRequest(BaseModel):
    product_id: UUID = Field(..., description="ID заказываемого товара")
    quantity: int = Field(
        default=1, gt=0, description="Количество товара (должно быть > 0)"
    )

    def to_dto(self) -> CreateOrderDto:
        return CreateOrderDto(
            product_id=self.product_id,
            quantity=self.quantity,
        )


class OrderFilterParams(BaseModel):
    user_id: UUID | None = Field(default=None, description="Фильтр по ID пользователя")
    status: OrderStatus | None = Field(
        default=None, description="Фильтр по статусу заказа"
    )
    offset: int = Field(default=0, ge=0, description="Смещение (offset)")
    limit: int = Field(default=50, ge=1, le=100, description="Лимит на страницу")

    def to_dto(self) -> OrderFilterDto:
        return OrderFilterDto(
            user_id=self.user_id,
            status=self.status,
            offset=self.offset,
            limit=self.limit,
        )


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: OrderResponseDto) -> "OrderResponse":
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            product_id=dto.product_id,
            quantity=dto.quantity,
            unit_price=dto.unit_price,
            total_amount=dto.total_amount,
            status=dto.status,
            created_at=dto.created_at,
        )


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    offset: int
    limit: int

    @classmethod
    def from_dto(cls, dto: OrderListResponseDto) -> "OrderListResponse":
        return cls(
            items=[OrderResponse.from_dto(o) for o in dto.items],
            total=dto.total,
            offset=dto.offset,
            limit=dto.limit,
        )
