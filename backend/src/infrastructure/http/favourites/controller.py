from uuid import UUID

from fastapi import APIRouter, status

from domain.user import UserRole
from infrastructure.http.auth.dependencies import require_roles
from infrastructure.http.middleware.authentication_middleware import CurrentUserDep

from .dependencies import FavouritesServiceDep
from .schemas import AddFavouriteRequest, FavouritesResponse

router = APIRouter(tags=["Favourites"])


def _get_favourites(
    user_id: UUID,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    dto = service.get_by_user_id(user_id)
    return FavouritesResponse.from_dto(dto)


def _add_to_favourites(
    user_id: UUID,
    request: AddFavouriteRequest,
    service: FavouritesServiceDep,
    added_by_user_id: UUID | None = None,
) -> FavouritesResponse:
    dto = service.add_product(
        user_id=user_id,
        dto=request.to_dto(),
        added_by_user_id=added_by_user_id or user_id,
    )
    return FavouritesResponse.from_dto(dto)


def _remove_from_favourites(
    user_id: UUID,
    product_id: UUID,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    dto = service.remove_product(
        user_id=user_id,
        product_id=product_id,
    )
    return FavouritesResponse.from_dto(dto)


def _clear_favourites(
    user_id: UUID,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    dto = service.clear(user_id)
    return FavouritesResponse.from_dto(dto)


@router.get(
    "/users/me/favourites",
    dependencies=[require_roles()],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список избранного текущего пользователя",
)
def get_favourites_me(
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _get_favourites(current_user.id, service)


@router.get(
    "/users/{user_id}/favourites",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить список избранного пользователя по ID (Admin)",
)
def get_favourites_by_user_id(
    user_id: UUID,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _get_favourites(user_id, service)


@router.post(
    "/users/me/favourites",
    dependencies=[require_roles()],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Добавить товар в избранное текущего пользователя",
)
def add_to_favourites_me(
    request: AddFavouriteRequest,
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _add_to_favourites(
        user_id=current_user.id,
        request=request,
        service=service,
        added_by_user_id=current_user.id,
    )


@router.post(
    "/users/{user_id}/favourites",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Добавить товар в избранное пользователя по ID (Admin)",
)
def add_to_favourites_by_user_id(
    user_id: UUID,
    request: AddFavouriteRequest,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _add_to_favourites(
        user_id=user_id,
        request=request,
        service=service,
    )


@router.delete(
    "/users/me/favourites/{product_id}",
    dependencies=[require_roles()],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить товар из избранного текущего пользователя",
)
def remove_from_favourites_me(
    product_id: UUID,
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _remove_from_favourites(current_user.id, product_id, service)


@router.delete(
    "/users/{user_id}/favourites/{product_id}",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить товар из избранного пользователя по ID (Admin)",
)
def remove_from_favourites_by_user_id(
    user_id: UUID,
    product_id: UUID,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _remove_from_favourites(user_id, product_id, service)


@router.delete(
    "/users/me/favourites",
    dependencies=[require_roles()],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Очистить всё избранное текущего пользователя",
)
def clear_favourites_me(
    current_user: CurrentUserDep,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _clear_favourites(current_user.id, service)


@router.delete(
    "/users/{user_id}/favourites",
    dependencies=[require_roles(UserRole.ADMIN)],
    response_model=FavouritesResponse,
    status_code=status.HTTP_200_OK,
    summary="Очистить всё избранное пользователя по ID (Admin)",
)
def clear_favourites_by_user_id(
    user_id: UUID,
    service: FavouritesServiceDep,
) -> FavouritesResponse:
    return _clear_favourites(user_id, service)
