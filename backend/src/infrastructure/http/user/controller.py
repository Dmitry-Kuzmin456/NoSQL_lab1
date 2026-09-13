from uuid import UUID

from fastapi import APIRouter, status

from infrastructure.http.user.schemas import (
    ChangePasswordRequest,
    RegisterUserRequest,
    UpdateUserRequest,
    UserResponse,
)

from .dependencies import UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
def register(
    request: RegisterUserRequest,
    service: UserServiceDep,
) -> UserResponse:
    user_dto = service.register(request.to_dto())
    return UserResponse.from_dto(user_dto)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по ID",
)
def get_by_id(
    user_id: UUID,
    service: UserServiceDep,
) -> UserResponse:
    user_dto = service.get_by_id(user_id)
    return UserResponse.from_dto(user_dto)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить профиль пользователя",
)
def update_profile(
    user_id: UUID,
    request: UpdateUserRequest,
    service: UserServiceDep,
) -> UserResponse:
    user_dto = service.update_profile(user_id, request.to_dto())
    return UserResponse.from_dto(user_dto)


@router.post(
    "/{user_id}/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Сменить пароль пользователя",
)
def change_password(
    user_id: UUID,
    request: ChangePasswordRequest,
    service: UserServiceDep,
) -> None:
    service.change_password(user_id, request.to_dto())


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
)
def delete_user(
    user_id: UUID,
    service: UserServiceDep,
) -> None:
    service.delete_user(user_id)
