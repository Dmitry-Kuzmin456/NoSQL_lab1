from fastapi import APIRouter, status

from .dependencies import RecoveryServiceDep
from .schemas import (
    MessageResponse,
    RecoveryResponse,
    RequestRecoveryRequest,
    ResetPasswordWithTokenRequest,
)

router = APIRouter(prefix="/recovery", tags=["Recovery"])


@router.post(
    "",
    response_model=RecoveryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Запросить токен для восстановления пароля по email",
)
def request_recovery_token(
    request: RequestRecoveryRequest,
    service: RecoveryServiceDep,
) -> RecoveryResponse:
    dto = service.create_token(request.to_dto())
    return RecoveryResponse.from_dto(dto)


@router.get(
    "/{token}",
    response_model=RecoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Проверить валидность токена восстановления",
)
def validate_recovery_token(
    token: str,
    service: RecoveryServiceDep,
) -> RecoveryResponse:
    dto = service.validate_token(token)
    return RecoveryResponse.from_dto(dto)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Сбросить пароль с использованием токена восстановления",
)
def reset_password(
    request: ResetPasswordWithTokenRequest,
    service: RecoveryServiceDep,
) -> MessageResponse:
    service.reset_password(request.to_dto())
    return MessageResponse(message="Пароль успешно изменен.")
