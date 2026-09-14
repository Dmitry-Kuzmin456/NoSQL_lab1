from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import HistoryServiceDep
from .schemas import UserHistoryResponse

router = APIRouter(tags=["History"])


def _get_history(
    user_id: UUID,
    service: HistoryServiceDep,
    offset: int,
    limit: int,
) -> UserHistoryResponse:
    dto = service.get_by_user_id(
        user_id=user_id,
        offset=offset,
        limit=limit,
    )
    return UserHistoryResponse.from_dto(dto)


def _clear_history(
    user_id: UUID,
    service: HistoryServiceDep,
) -> None:
    service.clear_user_history(user_id=user_id)


@router.get(
    "/users/me/history",
    response_model=UserHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить историю действий текущего пользователя",
)
def get_user_history_me(
    current_user: CurrentUserDep,
    service: HistoryServiceDep,
    offset: Annotated[
        int,
        Query(ge=0, description="Смещение (offset)"),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Количество событий на страницу (limit)"),
    ] = 20,
) -> UserHistoryResponse:
    return _get_history(
        user_id=current_user.id,
        service=service,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/users/{user_id}/history",
    response_model=UserHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить историю действий пользователя по ID (Admin)",
)
def get_user_history_by_user_id(
    user_id: UUID,
    service: HistoryServiceDep,
    offset: Annotated[
        int,
        Query(ge=0, description="Смещение (offset)"),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Количество событий на страницу (limit)"),
    ] = 20,
) -> UserHistoryResponse:
    return _get_history(
        user_id=user_id,
        service=service,
        offset=offset,
        limit=limit,
    )


@router.delete(
    "/users/me/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить историю действий текущего пользователя",
)
def clear_user_history_me(
    current_user: CurrentUserDep,
    service: HistoryServiceDep,
) -> None:
    _clear_history(user_id=current_user.id, service=service)


@router.delete(
    "/users/{user_id}/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить историю действий пользователя по ID (Admin)",
)
def clear_user_history_by_user_id(
    user_id: UUID,
    service: HistoryServiceDep,
) -> None:
    _clear_history(user_id=user_id, service=service)
