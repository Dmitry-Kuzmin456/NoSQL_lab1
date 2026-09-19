from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class FavouriteProduct:
    product_id: UUID
    added_user_id: UUID
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Favourites:
    user_id: UUID
    products: list[FavouriteProduct] = field(default_factory=list)
