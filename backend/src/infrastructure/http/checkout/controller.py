from uuid import UUID

from fastapi import APIRouter, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import CheckoutServiceDep
from .schemas import CheckoutResponse

router = APIRouter(tags=["Checkout"])


def _checkout(user_id: UUID, service: CheckoutServiceDep) -> CheckoutResponse:
    dto = service.checkout(user_id)
    return CheckoutResponse.from_dto(dto)


@router.post(
    "/users/me/checkout",
    response_model=CheckoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Оформить заказ из товаров в корзине текущего пользователя",
)
def checkout_cart_me(
    current_user: CurrentUserDep,
    service: CheckoutServiceDep,
) -> CheckoutResponse:
    return _checkout(current_user.id, service)


@router.post(
    "/users/{user_id}/checkout",
    response_model=CheckoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Оформить заказ из товаров в корзине пользователя по ID (Admin)",
)
def checkout_cart_by_user_id(
    user_id: UUID,
    service: CheckoutServiceDep,
) -> CheckoutResponse:
    return _checkout(user_id, service)
