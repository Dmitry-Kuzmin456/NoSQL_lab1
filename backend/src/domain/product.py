from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class Product:
    name: str
    description: str
    price: Decimal
    quantity: int
    id: UUID = field(default_factory=uuid4)

    def is_in_stock(self) -> bool:
        return self.quantity > 0

    def has_enough_stock(self, required_quantity: int) -> bool:
        return self.quantity >= required_quantity
