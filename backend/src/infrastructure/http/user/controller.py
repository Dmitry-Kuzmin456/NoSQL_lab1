from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from application.user import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    WeakNewPasswordException,
    WeakPasswordException,
)

from .dependencies import UserServiceDep
from .schemas import (
    ChangePasswordRequest,
    RegisterUserRequest,
    UpdateUserRequest,
    UserResponse,
)

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
    try:
        dto = request.to_dto()
        user_dto = service.register(dto)
        return UserResponse.from_dto(user_dto)
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except WeakPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


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
    try:
        user_dto = service.get_by_id(user_id)
        return UserResponse.from_dto(user_dto)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/by-email/{email}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по email",
)
def get_by_email(
    email: str,
    service: UserServiceDep,
) -> UserResponse:
    try:
        user_dto = service.get_by_email(email)
        return UserResponse.from_dto(user_dto)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


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
    try:
        dto = request.to_dto()
        user_dto = service.update_profile(user_id, dto)
        return UserResponse.from_dto(user_dto)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


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
    try:
        dto = request.to_dto()
        service.change_password(user_id, dto)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except WeakNewPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
)
def delete_user(
    user_id: UUID,
    service: UserServiceDep,
) -> None:
    try:
        service.delete_user(user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
