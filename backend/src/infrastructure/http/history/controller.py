from typing import Annotated

from fastapi import APIRouter, Query, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import HistoryServiceDep
from .schemas import UserHistoryResponse

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=UserHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить историю действий текущего пользователя",
)
def get_user_history(
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
    dto = service.get_by_user_id(
        user_id=current_user.id,
        offset=offset,
        limit=limit,
    )
    return UserHistoryResponse.from_dto(dto)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить историю действий текущего пользователя",
)
def clear_user_history(
    current_user: CurrentUserDep,
    service: HistoryServiceDep,
) -> None:
    service.clear_user_history(user_id=current_user.id)
