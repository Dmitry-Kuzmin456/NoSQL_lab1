from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4


class OrderStatus(StrEnum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    user_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    id: UUID = field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.CREATED
    total_amount: Decimal = field(default=Decimal("0.00"))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price < Decimal("0.00"):
            raise ValueError("Unit price cannot be negative")
        if self.total_amount == Decimal("0.00"):
            self.total_amount = self.unit_price * Decimal(self.quantity)

    def cancel(self) -> None:
        if self.status != OrderStatus.CREATED:
            raise ValueError(f"Cannot cancel order with status {self.status}")
        self.status = OrderStatus.CANCELLED

    def approve(self) -> None:
        if self.status != OrderStatus.CREATED:
            raise ValueError(f"Cannot approve order with status {self.status}")
        self.status = OrderStatus.APPROVED

    def reject(self) -> None:
        if self.status != OrderStatus.CREATED:
            raise ValueError(f"Cannot reject order with status {self.status}")
        self.status = OrderStatus.REJECTED
