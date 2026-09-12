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

    def add_product(self, product_id: UUID, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        for item in self.cart_products:
            if item.product_id == product_id:
                item.quantity += quantity
                item.updated_at = datetime.now(UTC)
                return
        self.cart_products.append(CartProduct(product_id=product_id, quantity=quantity))

    def update_quantity(self, product_id: UUID, quantity: int) -> None:
        if quantity <= 0:
            self.remove_product(product_id)
            return
        for item in self.cart_products:
            if item.product_id == product_id:
                item.quantity = quantity
                item.updated_at = datetime.now(UTC)
                return
        self.cart_products.append(CartProduct(product_id=product_id, quantity=quantity))

    def remove_product(self, product_id: UUID) -> None:
        self.cart_products = [
            p for p in self.cart_products if p.product_id != product_id
        ]

    def clear(self) -> None:
        self.cart_products.clear()

    def get_total_items(self) -> int:
        return sum(p.quantity for p in self.cart_products)
