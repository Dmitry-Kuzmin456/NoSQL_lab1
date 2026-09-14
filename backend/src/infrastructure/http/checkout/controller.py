from fastapi import APIRouter, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import CheckoutServiceDep
from .schemas import CheckoutResponse

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post(
    "",
    response_model=CheckoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Оформить заказ из товаров в корзине",
)
def checkout_cart(
    current_user: CurrentUserDep,
    service: CheckoutServiceDep,
) -> CheckoutResponse:
    dto = service.checkout(current_user.id)
    return CheckoutResponse.from_dto(dto)
