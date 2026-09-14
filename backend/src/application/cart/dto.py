from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.cart import Cart, CartProduct


@dataclass(frozen=True)
class AddCartProductDto:
    product_id: UUID
    quantity: int = 1


@dataclass(frozen=True)
class UpdateCartProductDto:
    product_id: UUID
    quantity: int


@dataclass(frozen=True)
class CartItemResponseDto:
    product_id: UUID
    quantity: int
    updated_at: datetime

    @classmethod
    def from_domain(cls, item: CartProduct) -> "CartItemResponseDto":
        return cls(
            product_id=item.product_id,
            quantity=item.quantity,
            updated_at=item.updated_at,
        )


@dataclass(frozen=True)
class CartResponseDto:
    user_id: UUID
    items: list[CartItemResponseDto]
    total_items: int

    @classmethod
    def from_domain(cls, cart: Cart) -> "CartResponseDto":
        items = [CartItemResponseDto.from_domain(p) for p in cart.cart_products]
        return cls(
            user_id=cart.user_id,
            items=items,
            total_items=cart.get_total_items(),
        )
