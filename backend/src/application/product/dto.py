from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.product import Product


@dataclass(frozen=True)
class ProductCreateDto:
    name: str
    description: str
    price: Decimal
    quantity: int = 0


@dataclass(frozen=True)
class ProductUpdateDto:
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    quantity: int | None = None


@dataclass(frozen=True)
class ProductFilterDto:
    query: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    in_stock_only: bool = False
    offset: int = 0
    limit: int = 50

    def matches(self, product: Product) -> bool:
        if self.query is not None and self.query.strip():
            q = self.query.strip().lower()
            if q not in product.name.lower() and q not in product.description.lower():
                return False
        if self.min_price is not None and product.price < self.min_price:
            return False
        if self.max_price is not None and product.price > self.max_price:
            return False
        return not (self.in_stock_only and not product.is_in_stock())

    def apply(self, products: list[Product]) -> tuple[list[Product], int]:
        filtered = [p for p in products if self.matches(p)]
        total = len(filtered)
        paginated = filtered[self.offset : self.offset + self.limit]
        return paginated, total


@dataclass(frozen=True)
class ProductResponseDto:
    id: UUID
    name: str
    description: str
    price: Decimal
    quantity: int
    is_in_stock: bool

    @classmethod
    def from_domain(cls, product: Product) -> "ProductResponseDto":
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            is_in_stock=product.is_in_stock(),
        )


@dataclass(frozen=True)
class ProductListResponseDto:
    items: list[ProductResponseDto]
    total: int
    offset: int
    limit: int
