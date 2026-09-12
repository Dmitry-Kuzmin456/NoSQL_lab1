from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from application.session.exceptions import (
    SessionExpiredException,
    SessionNotFoundException,
    SessionRevokedException,
)
from application.user.exceptions import InvalidCredentialsException

from .dependencies import AuthServiceDep
from .schemas import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    SessionResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя и создание сессии",
)
def login(
    request: LoginRequest,
    service: AuthServiceDep,
) -> AuthResponse:
    try:
        dto = request.to_dto()
        auth_dto = service.login(dto)
        return AuthResponse.from_dto(auth_dto)
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление refresh-токена сессии",
)
def refresh(
    request: RefreshTokenRequest,
    service: AuthServiceDep,
) -> SessionResponse:
    try:
        session_dto = service.refresh(request.refresh_token)
        return SessionResponse.from_dto(session_dto)
    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except SessionRevokedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except SessionExpiredException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/logout/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Завершение конкретной сессии (logout)",
)
def logout(
    session_id: UUID,
    service: AuthServiceDep,
) -> None:
    try:
        service.logout(session_id)
    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/logout-all/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Завершение всех активных сессий пользователя",
)
def logout_all(
    user_id: UUID,
    service: AuthServiceDep,
) -> None:
    service.logout_all(user_id)
