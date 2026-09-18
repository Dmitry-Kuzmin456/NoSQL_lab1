from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from application.product.dto import (
    ProductCreateDto,
    ProductListResponseDto,
    ProductResponseDto,
    ProductUpdateDto,
)


class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Ноутбук ThinkPad"])
    description: str = Field(
        default="", max_length=2000, examples=["Ноутбук для программирования и учебы"]
    )
    price: Decimal = Field(..., ge=0, examples=[Decimal("79990.00")])
    quantity: int = Field(default=0, ge=0, examples=[10])

    def to_dto(self) -> ProductCreateDto:
        return ProductCreateDto(
            name=self.name,
            description=self.description,
            price=self.price,
            quantity=self.quantity,
        )


class UpdateProductRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)

    def to_dto(self) -> ProductUpdateDto:
        return ProductUpdateDto(
            name=self.name,
            description=self.description,
            price=self.price,
            quantity=self.quantity,
        )


class StockOperationRequest(BaseModel):
    amount: int = Field(..., gt=0, examples=[1])


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    quantity: int
    is_in_stock: bool

    @classmethod
    def from_dto(cls, dto: ProductResponseDto) -> "ProductResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            price=dto.price,
            quantity=dto.quantity,
            is_in_stock=dto.is_in_stock,
        )


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    offset: int
    limit: int

    @classmethod
    def from_dto(cls, dto: ProductListResponseDto) -> "ProductListResponse":
        return cls(
            items=[ProductResponse.from_dto(p) for p in dto.items],
            offset=dto.offset,
            limit=dto.limit,
        )
