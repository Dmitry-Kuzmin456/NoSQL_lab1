from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from application.product.dto import ProductResponseDto
from domain.cart import Cart, CartProduct


@dataclass(frozen=True)
class UpdateCartProductDto:
    product_id: UUID
    quantity: int


@dataclass(frozen=True)
class CartItemResponseDto:
    product_id: UUID
    quantity: int
    updated_at: datetime
    product: ProductResponseDto | None = None
    unit_price: Decimal = Decimal("0.00")
    subtotal: Decimal = Decimal("0.00")
    is_available: bool = True
    available_stock: int = 0

    @classmethod
    def from_domain(
        cls,
        item: CartProduct,
        product: ProductResponseDto | None = None,
        is_available: bool = True,
        available_stock: int = 0,
        unit_price: Decimal = Decimal("0.00"),
        subtotal: Decimal = Decimal("0.00"),
    ) -> "CartItemResponseDto":
        return cls(
            product_id=item.product_id,
            quantity=item.quantity,
            updated_at=item.updated_at,
            product=product,
            unit_price=unit_price,
            subtotal=subtotal,
            is_available=is_available,
            available_stock=available_stock,
        )


@dataclass(frozen=True)
class CartResponseDto:
    user_id: UUID
    items: list[CartItemResponseDto]
    total_items: int
    total_amount: Decimal = Decimal("0.00")
    has_unavailable_items: bool = False

    @classmethod
    def from_domain(
        cls,
        cart: Cart,
        items: list[CartItemResponseDto] | None = None,
        total_amount: Decimal = Decimal("0.00"),
        has_unavailable_items: bool = False,
    ) -> "CartResponseDto":
        if items is None:
            items = [CartItemResponseDto.from_domain(p) for p in cart.cart_products]
        return cls(
            user_id=cart.user_id,
            items=items,
            total_items=cart.get_total_items(),
            total_amount=total_amount,
            has_unavailable_items=has_unavailable_items,
        )

