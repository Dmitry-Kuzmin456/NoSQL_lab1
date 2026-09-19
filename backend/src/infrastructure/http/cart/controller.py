from uuid import UUID

from fastapi import APIRouter, status

from domain.user import UserRole
from infrastructure.http.auth.dependencies import require_roles
from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import CartServiceDep
from .schemas import (
    CartResponse,
    UpdateCartItemRequest,
)

router = APIRouter(tags=["Cart"])


def _get_cart(user_id: UUID, service: CartServiceDep) -> CartResponse:
    dto = service.get_by_user_id(user_id)
    return CartResponse.from_dto(dto)


def _update_quantity(
    user_id: UUID,
    product_id: UUID,
    request: UpdateCartItemRequest,
    service: CartServiceDep,
) -> CartResponse:
    dto = service.update_quantity(
        user_id=user_id,
        dto=request.to_dto(product_id),
    )
    return CartResponse.from_dto(dto)


def _remove_product(
    user_id: UUID,
    product_id: UUID,
    service: CartServiceDep,
) -> CartResponse:
    dto = service.remove_product(
        user_id=user_id,
        product_id=product_id,
    )
    return CartResponse.from_dto(dto)


def _clear(user_id: UUID, service: CartServiceDep) -> CartResponse:
    dto = service.clear(user_id)
    return CartResponse.from_dto(dto)


@router.get(
    "/users/me/cart",
    dependencies=[require_roles()],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить корзину текущего пользователя",
)
def get_cart_me(
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    return _get_cart(current_user.id, service)


@router.get(
    "/users/{user_id}/cart",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить корзину пользователя по ID (Admin)",
)
def get_cart_by_user_id(
    user_id: UUID,
    service: CartServiceDep,
) -> CartResponse:
    return _get_cart(user_id, service)


@router.patch(
    "/users/me/cart/items/{product_id}",
    dependencies=[require_roles()],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить количество товара в корзине текущего пользователя",
)
def update_cart_item_me(
    product_id: UUID,
    request: UpdateCartItemRequest,
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    return _update_quantity(current_user.id, product_id, request, service)


@router.patch(
    "/users/{user_id}/cart/items/{product_id}",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить количество товара в корзине пользователя по ID (Admin)",
)
def update_cart_item_by_user_id(
    user_id: UUID,
    product_id: UUID,
    request: UpdateCartItemRequest,
    service: CartServiceDep,
) -> CartResponse:
    return _update_quantity(user_id, product_id, request, service)


@router.delete(
    "/users/me/cart/items/{product_id}",
    dependencies=[require_roles()],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить товар из корзины текущего пользователя",
)
def remove_cart_item_me(
    product_id: UUID,
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    return _remove_product(current_user.id, product_id, service)


@router.delete(
    "/users/{user_id}/cart/items/{product_id}",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить товар из корзины пользователя по ID (Admin)",
)
def remove_cart_item_by_user_id(
    user_id: UUID,
    product_id: UUID,
    service: CartServiceDep,
) -> CartResponse:
    return _remove_product(user_id, product_id, service)


@router.delete(
    "/users/me/cart",
    dependencies=[require_roles()],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Очистить корзину текущего пользователя",
)
def clear_cart_me(
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartResponse:
    return _clear(current_user.id, service)


@router.delete(
    "/users/{user_id}/cart",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Очистить корзину пользователя по ID (Admin)",
)
def clear_cart_by_user_id(
    user_id: UUID,
    service: CartServiceDep,
) -> CartResponse:
    return _clear(user_id, service)
