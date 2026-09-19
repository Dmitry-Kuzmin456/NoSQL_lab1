from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class CartProduct:
    product_id: UUID
    quantity: int
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Cart:
    user_id: UUID
    cart_products: list[CartProduct] = field(default_factory=list)

    def has_product(self, product_id: UUID) -> bool:
        return any(p.product_id == product_id for p in self.cart_products)

    def get_total_items(self) -> int:
        return sum(p.quantity for p in self.cart_products)
