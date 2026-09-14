from uuid import UUID

from application.event_bus import IEventBus
from application.product.service import ProductService
from domain.cart import Cart
from domain.history import OperationEvent, OperationType

from .dto import (
    AddCartProductDto,
    CartResponseDto,
    UpdateCartProductDto,
)
from .exceptions import (
    CartProductNotFoundException,
    InvalidCartQuantityException,
)
from .repository import ICartRepository


class CartService:
    def __init__(
        self,
        cart_repository: ICartRepository,
        product_service: ProductService,
        event_bus: IEventBus,
    ) -> None:
        self._cart_repository = cart_repository
        self._product_service = product_service
        self._event_bus = event_bus

    def get_by_user_id(self, user_id: UUID) -> CartResponseDto:
        cart = self._get_or_create(user_id)
        return CartResponseDto.from_domain(cart)

    def add_product(
        self,
        user_id: UUID,
        dto: AddCartProductDto,
    ) -> CartResponseDto:
        if dto.quantity <= 0:
            raise InvalidCartQuantityException()

        self._product_service.get_by_id(dto.product_id)

        cart = self._get_or_create(user_id)
        cart.add_product(dto.product_id, dto.quantity)

        saved = self._cart_repository.save(cart)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.ADD_CART_ITEM,
                target_id=dto.product_id,
                details={"quantity": dto.quantity},
            )
        )

        return CartResponseDto.from_domain(saved)

    def update_quantity(
        self,
        user_id: UUID,
        dto: UpdateCartProductDto,
    ) -> CartResponseDto:
        cart = self._get_or_create(user_id)
        if not cart.has_product(dto.product_id):
            raise CartProductNotFoundException(dto.product_id)

        cart.update_quantity(dto.product_id, dto.quantity)
        saved = self._cart_repository.save(cart)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.UPDATE_CART_ITEM,
                target_id=dto.product_id,
                details={"new_quantity": dto.quantity},
            )
        )

        return CartResponseDto.from_domain(saved)

    def remove_product(
        self,
        user_id: UUID,
        product_id: UUID,
    ) -> CartResponseDto:
        cart = self._get_or_create(user_id)
        if not cart.has_product(product_id):
            raise CartProductNotFoundException(product_id)

        cart.remove_product(product_id)
        saved = self._cart_repository.save(cart)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.REMOVE_CART_ITEM,
                target_id=product_id,
            )
        )

        return CartResponseDto.from_domain(saved)

    def clear(self, user_id: UUID) -> CartResponseDto:
        cart = self._get_or_create(user_id)
        cart.clear()
        saved = self._cart_repository.save(cart)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.CLEAR_CART,
            )
        )

        return CartResponseDto.from_domain(saved)

    def _get_or_create(self, user_id: UUID) -> Cart:
        cart = self._cart_repository.get_by_user_id(user_id)
        if cart is None:
            cart = Cart(user_id=user_id)
        return cart
