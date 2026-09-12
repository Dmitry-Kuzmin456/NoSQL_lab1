from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


@dataclass
class FavouriteProduct:
    product_id: UUID
    added_user_id: UUID
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note: str | None = None


@dataclass
class Favourites:
    user_id: UUID
    products: list[FavouriteProduct] = field(default_factory=list)

    def add_product(self, product_id: UUID, added_user_id: UUID, note: str | None = None) -> None:
        for item in self.products:
            if item.product_id == product_id:
                item.note = note
                item.updated_at = datetime.now(timezone.utc)
                return
        self.products.append(
            FavouriteProduct(product_id=product_id, added_user_id=added_user_id, note=note)
        )

    def remove_product(self, product_id: UUID) -> None:
        self.products = [p for p in self.products if p.product_id != product_id]

    def has_product(self, product_id: UUID) -> bool:
        return any(p.product_id == product_id for p in self.products)

    def clear(self) -> None:
        self.products.clear()