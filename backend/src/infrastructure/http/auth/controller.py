from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from application.session.exceptions import (
    SessionException,
    SessionExpiredException,
    SessionNotFoundException,
    SessionRevokedException,
)
from application.user.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
)
from infrastructure.environment.settings import settings
from infrastructure.http.user.schemas import UserResponse

from .dependencies import AuthServiceDep
from .schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


def _set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=settings.auth.cookie_httponly,
        samesite=settings.auth.cookie_samesite,
        secure=settings.auth.cookie_secure,
        max_age=settings.auth.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.auth.cookie_httponly,
        samesite=settings.auth.cookie_samesite,
        secure=settings.auth.cookie_secure,
        max_age=settings.auth.refresh_token_expire_days * 86400,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")


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
    try:
        dto = request.to_dto()
        auth_dto = service.login(dto)
        _set_auth_cookies(
            response=response,
            access_token=auth_dto.access_token,
            refresh_token=auth_dto.session.refresh_token,
        )
        return UserResponse.from_dto(auth_dto.user)
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


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
    try:
        auth_dto = service.refresh(refresh_token)
        _set_auth_cookies(
            response=response,
            access_token=auth_dto.access_token,
            refresh_token=auth_dto.session.refresh_token,
        )
        return UserResponse.from_dto(auth_dto.user)
    except (SessionNotFoundException, UserNotFoundException) as e:
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (SessionRevokedException, SessionExpiredException) as e:
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


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
    _clear_auth_cookies(response)


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
    _clear_auth_cookies(response)
