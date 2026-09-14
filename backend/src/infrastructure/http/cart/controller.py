from uuid import UUID

from fastapi import APIRouter, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import CartServiceDep
from .schemas import (
    AddCartItemRequest,
    CartResponse,
    UpdateCartItemRequest,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить корзину текущего пользователя",
)
def get_cart(
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    dto = service.get_by_user_id(current_user.id)
    return CartResponse.from_dto(dto)


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Добавить товар в корзину",
)
def add_item_to_cart(
    request: AddCartItemRequest,
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    dto = service.add_product(
        user_id=current_user.id,
        dto=request.to_dto(),
    )
    return CartResponse.from_dto(dto)


@router.patch(
    "/items/{product_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить количество товара в корзине",
)
def update_cart_item(
    product_id: UUID,
    request: UpdateCartItemRequest,
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    dto = service.update_quantity(
        user_id=current_user.id,
        dto=request.to_dto(product_id),
    )
    return CartResponse.from_dto(dto)


@router.delete(
    "/items/{product_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить товар из корзины",
)
def remove_cart_item(
    product_id: UUID,
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    dto = service.remove_product(
        user_id=current_user.id,
        product_id=product_id,
    )
    return CartResponse.from_dto(dto)


@router.delete(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Очистить корзину",
)
def clear_cart(
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    dto = service.clear(current_user.id)
    return CartResponse.from_dto(dto)
