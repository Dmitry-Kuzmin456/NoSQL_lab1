from uuid import UUID

from fastapi import APIRouter, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import FavouritesServiceDep
from .schemas import AddFavouriteRequest, FavouritesResponse

router = APIRouter(prefix="/favourites", tags=["Favourites"])


@router.get(
    "",
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список избранного текущего пользователя",
)
def get_favourites(
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    dto = service.get_by_user_id(current_user.id)
    return FavouritesResponse.from_dto(dto)


@router.post(
    "",
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Добавить товар в избранное",
)
def add_to_favourites(
    request: AddFavouriteRequest,
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    dto = service.add_product(
        user_id=current_user.id,
        dto=request.to_dto(),
        added_by_user_id=current_user.id,
    )
    return FavouritesResponse.from_dto(dto)


@router.delete(
    "/{product_id}",
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить товар из избранного",
)
def remove_from_favourites(
    product_id: UUID,
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    dto = service.remove_product(
        user_id=current_user.id,
        product_id=product_id,
    )
    return FavouritesResponse.from_dto(dto)


@router.delete(
    "",
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Очистить всё избранное",
)
def clear_favourites(
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    dto = service.clear(current_user.id)
    return FavouritesResponse.from_dto(dto)
