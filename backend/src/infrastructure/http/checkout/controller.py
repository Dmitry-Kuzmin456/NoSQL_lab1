from uuid import UUID

from fastapi import APIRouter, status

from domain.user import UserRole
from infrastructure.http.auth.dependencies import require_roles
from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import CheckoutServiceDep
from .schemas import CheckoutResponse

router = APIRouter(tags=["Checkout"])


def _checkout(user_id: UUID, service: CheckoutServiceDep) -> CheckoutResponse:
    dto = service.checkout(user_id)
    return CheckoutResponse.from_dto(dto)


@router.post(
    "/users/me/checkout",
    dependencies=[require_roles()],
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
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=CheckoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Оформить заказ из товаров в корзине пользователя по ID (Admin)",
)
def checkout_cart_by_user_id(
    user_id: UUID,
    service: CheckoutServiceDep,
) -> CheckoutResponse:
    return _checkout(user_id, service)
