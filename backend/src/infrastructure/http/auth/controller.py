from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Response, status

from application.session.exceptions import SessionException
from infrastructure.http.auth.cookies import CookieManager
from infrastructure.http.user.schemas import UserResponse

from .dependencies import AuthServiceDep
from .schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя и установка auth-cookie",
)
def login(
    request: LoginRequest,
    response: Response,
    service: AuthServiceDep,
) -> UserResponse:
    auth_dto = service.login(request.to_dto())
    CookieManager.set_auth_cookies(
        response=response,
        access_token=auth_dto.access_token,
        refresh_token=auth_dto.session.refresh_token,
    )
    return UserResponse.from_dto(auth_dto.user)


@router.post(
    "/refresh",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов через обязательный cookie",
)
def refresh(
    response: Response,
    service: AuthServiceDep,
    refresh_token: Annotated[str, Cookie(alias="refresh_token")],
) -> UserResponse:
    auth_dto = service.refresh(refresh_token)
    CookieManager.set_auth_cookies(
        response=response,
        access_token=auth_dto.access_token,
        refresh_token=auth_dto.session.refresh_token,
    )
    return UserResponse.from_dto(auth_dto.user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы (отзыв текущей сессии и очистка cookie)",
)
def logout(
    response: Response,
    service: AuthServiceDep,
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> None:
    if refresh_token:
        try:
            service.logout_by_refresh_token(refresh_token)
        except SessionException:
            pass
    CookieManager.clear_auth_cookies(response)


@router.post(
    "/logout-all/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Завершение всех активных сессий пользователя и очистка cookie",
)
def logout_all(
    user_id: UUID,
    response: Response,
    service: AuthServiceDep,
) -> None:
    service.logout_all(user_id)
    CookieManager.clear_auth_cookies(response)
