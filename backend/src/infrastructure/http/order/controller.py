from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import OrderServiceDep
from .schemas import (
    CreateOrderRequest,
    OrderFilterParams,
    OrderListResponse,
    OrderResponse,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый заказ",
)
def create_order(
    request: CreateOrderRequest,
    current_user: CurrentUserDep,
    service: OrderServiceDep,
) -> OrderResponse:
    dto = service.create(
        user_id=current_user.id,
        dto=request.to_dto(),
    )
    return OrderResponse.from_dto(dto)


@router.get(
    "",
    response_model=OrderListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список заказов",
)
def list_orders(
    service: OrderServiceDep,
    filters: Annotated[OrderFilterParams, Query()],
) -> OrderListResponse:
    result = service.list(filters.to_dto())
    return OrderListResponse.from_dto(result)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о заказе по ID",
)
def get_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> OrderResponse:
    dto = service.get_by_id(order_id)
    return OrderResponse.from_dto(dto)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Отменить заказ",
)
def cancel_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> OrderResponse:
    dto = service.cancel(order_id)
    return OrderResponse.from_dto(dto)


@router.post(
    "/{order_id}/approve",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Подтвердить заказ",
)
def approve_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> OrderResponse:
    dto = service.approve(order_id)
    return OrderResponse.from_dto(dto)


@router.post(
    "/{order_id}/reject",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Отклонить заказ",
)
def reject_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> OrderResponse:
    dto = service.reject(order_id)
    return OrderResponse.from_dto(dto)
