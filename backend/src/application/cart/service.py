from uuid import UUID

from application.event_bus import IEventBus
from application.product.service import ProductService
from domain.cart import Cart
from domain.history import OperationEvent, OperationType

from .dto import (
    CartResponseDto,
    UpdateCartProductDto,
)
from .exceptions import (
    CartProductNotFoundException,
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

    def is_in_cart(self, user_id: UUID, product_id: UUID) -> bool:
        cart = self._cart_repository.get_by_user_id(user_id)
        if cart is None:
            return False
        return cart.has_product(product_id)

    def update_quantity(
        self,
        user_id: UUID,
        dto: UpdateCartProductDto,
    ) -> CartResponseDto:
        if dto.quantity <= 0:
            cart = self._cart_repository.remove_item_and_get(user_id, dto.product_id)
        else:
            self._product_service.ensure_exists(dto.product_id)
            cart = self._cart_repository.set_item_quantity_and_get(
                user_id=user_id,
                product_id=dto.product_id,
                quantity=dto.quantity,
            )

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.UPDATE_CART_ITEM,
                target_id=dto.product_id,
                details={"new_quantity": dto.quantity},
            )
        )

        return CartResponseDto.from_domain(cart)

    def remove_product(
        self,
        user_id: UUID,
        product_id: UUID,
    ) -> CartResponseDto:
        cart = self._get_or_create(user_id)
        if not cart.has_product(product_id):
            raise CartProductNotFoundException(product_id)

        updated_cart = self._cart_repository.remove_item_and_get(user_id, product_id)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.REMOVE_CART_ITEM,
                target_id=product_id,
            )
        )

        return CartResponseDto.from_domain(updated_cart)

    def clear(self, user_id: UUID) -> CartResponseDto:
        self._cart_repository.delete_by_user_id(user_id)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.CLEAR_CART,
            )
        )

        return CartResponseDto.from_domain(Cart(user_id=user_id))

    def _get_or_create(self, user_id: UUID) -> Cart:
        cart = self._cart_repository.get_by_user_id(user_id)
        if cart is None:
            cart = Cart(user_id=user_id)
        return cart
