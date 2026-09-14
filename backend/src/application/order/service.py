from uuid import UUID

from application.event_bus import IEventBus
from application.product.service import ProductService
from domain.history import OperationEvent, OperationType
from domain.order import Order, OrderStatus

from .dto import (
    CreateOrderDto,
    OrderFilterDto,
    OrderListResponseDto,
    OrderResponseDto,
)
from .exceptions import (
    InvalidOrderQuantityException,
    InvalidOrderStatusException,
    OrderNotFoundException,
)
from .repository import IOrderRepository


class OrderService:
    def __init__(
        self,
        order_repository: IOrderRepository,
        product_service: ProductService,
        event_bus: IEventBus,
    ) -> None:
        self._order_repository = order_repository
        self._product_service = product_service
        self._event_bus = event_bus

    def create(self, user_id: UUID, dto: CreateOrderDto) -> OrderResponseDto:
        if dto.quantity <= 0:
            raise InvalidOrderQuantityException()

        product = self._product_service.get_by_id(dto.product_id)

        self._product_service.reserve_stock(dto.product_id, dto.quantity)

        order = Order(
            user_id=user_id,
            product_id=dto.product_id,
            quantity=dto.quantity,
            unit_price=product.price,
        )

        saved = self._order_repository.save(order)
        self._order_repository.increment_orders_count()

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.CREATE_ORDER,
                target_id=saved.id,
                details={
                    "product_id": str(saved.product_id),
                    "quantity": saved.quantity,
                    "total_amount": f"{saved.total_amount:.2f}",
                },
            )
        )

        return OrderResponseDto.from_domain(saved)

    def get_by_id(self, order_id: UUID) -> OrderResponseDto:
        order = self._order_repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundException(order_id)

        return OrderResponseDto.from_domain(order)

    def list(
        self,
        filter_dto: OrderFilterDto | None = None,
    ) -> OrderListResponseDto:
        if filter_dto is None:
            filter_dto = OrderFilterDto()

        items, total = self._order_repository.list(filter_dto=filter_dto)
        return OrderListResponseDto(
            items=[OrderResponseDto.from_domain(o) for o in items],
            total=total,
            offset=filter_dto.offset,
            limit=filter_dto.limit,
        )

    def list_user_orders(
        self,
        user_id: UUID,
        status: OrderStatus | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> OrderListResponseDto:
        filter_dto = OrderFilterDto(
            user_id=user_id,
            status=status,
            offset=offset,
            limit=limit,
        )
        return self.list(filter_dto)

    def cancel(self, order_id: UUID) -> OrderResponseDto:
        if not self._order_repository.exists_by_id(order_id):
            raise OrderNotFoundException(order_id)

        if not self._order_repository.update_status(
            order_id, OrderStatus.CANCELLED, expected_status=OrderStatus.CREATED
        ):
            order = self._order_repository.get_by_id(order_id)
            status = order.status if order else "UNKNOWN"
            raise InvalidOrderStatusException(f"Cannot cancel order with status {status}")

        order = self._order_repository.get_by_id(order_id)
        assert order is not None

        self._product_service.restore_stock(order.product_id, order.quantity)

        self._event_bus.publish(
            OperationEvent(
                user_id=order.user_id,
                action=OperationType.CANCEL_ORDER,
                target_id=order.id,
                details={
                    "product_id": str(order.product_id),
                    "quantity": order.quantity,
                },
            )
        )

        return OrderResponseDto.from_domain(order)

    def approve(self, order_id: UUID) -> OrderResponseDto:
        if not self._order_repository.exists_by_id(order_id):
            raise OrderNotFoundException(order_id)

        if not self._order_repository.update_status(
            order_id, OrderStatus.APPROVED, expected_status=OrderStatus.CREATED
        ):
            order = self._order_repository.get_by_id(order_id)
            status = order.status if order else "UNKNOWN"
            raise InvalidOrderStatusException(f"Cannot approve order with status {status}")

        order = self._order_repository.get_by_id(order_id)
        assert order is not None

        self._event_bus.publish(
            OperationEvent(
                user_id=order.user_id,
                action=OperationType.APPROVE_ORDER,
                target_id=order.id,
            )
        )

        return OrderResponseDto.from_domain(order)

    def reject(self, order_id: UUID) -> OrderResponseDto:
        if not self._order_repository.exists_by_id(order_id):
            raise OrderNotFoundException(order_id)

        if not self._order_repository.update_status(
            order_id, OrderStatus.REJECTED, expected_status=OrderStatus.CREATED
        ):
            order = self._order_repository.get_by_id(order_id)
            status = order.status if order else "UNKNOWN"
            raise InvalidOrderStatusException(f"Cannot reject order with status {status}")

        order = self._order_repository.get_by_id(order_id)
        assert order is not None

        self._product_service.restore_stock(order.product_id, order.quantity)

        self._event_bus.publish(
            OperationEvent(
                user_id=order.user_id,
                action=OperationType.REJECT_ORDER,
                target_id=order.id,
            )
        )

        return OrderResponseDto.from_domain(order)

    def get_total_orders_count(self) -> int:
        return self._order_repository.get_total_orders_count()
