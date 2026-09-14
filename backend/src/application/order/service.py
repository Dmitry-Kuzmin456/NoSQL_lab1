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
        order = self._order_repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundException(order_id)

        try:
            order.cancel()
        except ValueError as exc:
            raise InvalidOrderStatusException(str(exc)) from exc

        self._product_service.restore_stock(order.product_id, order.quantity)

        saved = self._order_repository.save(order)

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

        return OrderResponseDto.from_domain(saved)

    def approve(self, order_id: UUID) -> OrderResponseDto:
        order = self._order_repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundException(order_id)

        try:
            order.approve()
        except ValueError as exc:
            raise InvalidOrderStatusException(str(exc)) from exc

        saved = self._order_repository.save(order)

        self._event_bus.publish(
            OperationEvent(
                user_id=order.user_id,
                action=OperationType.APPROVE_ORDER,
                target_id=order.id,
            )
        )

        return OrderResponseDto.from_domain(saved)

    def reject(self, order_id: UUID) -> OrderResponseDto:
        order = self._order_repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundException(order_id)

        try:
            order.reject()
        except ValueError as exc:
            raise InvalidOrderStatusException(str(exc)) from exc

        self._product_service.restore_stock(order.product_id, order.quantity)

        saved = self._order_repository.save(order)

        self._event_bus.publish(
            OperationEvent(
                user_id=order.user_id,
                action=OperationType.REJECT_ORDER,
                target_id=order.id,
            )
        )

        return OrderResponseDto.from_domain(saved)
