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

    def reserve_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount to reserve must be positive")
        if not self.has_enough_stock(amount):
            raise ValueError(f"Not enough stock for product {self.name}: requested {amount}, available {self.quantity}")
        self.quantity -= amount

    def restore_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount to restore must be positive")
        self.quantity += amount


