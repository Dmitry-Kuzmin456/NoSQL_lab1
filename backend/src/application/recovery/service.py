from datetime import UTC, datetime, timedelta
from uuid import UUID

from application.user.service import UserService
from domain.recovery_token import RecoveryToken

from .dto import (
    CreateRecoveryDto,
    RecoveryResponseDto,
    ResetPasswordWithTokenDto,
)
from .exceptions import (
    RecoveryTokenAlreadyUsedException,
    RecoveryTokenExpiredException,
    RecoveryTokenNotFoundException,
)
from .repository import IRecoveryTokenRepository


class RecoveryService:
    def __init__(
        self,
        recovery_token_repository: IRecoveryTokenRepository,
        user_service: UserService,
    ) -> None:
        self._recovery_token_repository = recovery_token_repository
        self._user_service = user_service

    def create_token(
        self, dto: CreateRecoveryDto, ttl_minutes: int = 15
    ) -> RecoveryResponseDto:
        user = self._user_service.get_by_email(dto.email)
        expires_at = datetime.now(UTC) + timedelta(minutes=ttl_minutes)

        recovery_token = RecoveryToken(
            user_id=user.id,
            expires_at=expires_at,
        )

        saved_token = self._recovery_token_repository.save(recovery_token)
        return RecoveryResponseDto.from_domain(saved_token)

    def create_token_for_user(
        self, user_id: UUID, ttl_minutes: int = 15
    ) -> RecoveryResponseDto:
        user = self._user_service.get_by_id(user_id)
        expires_at = datetime.now(UTC) + timedelta(minutes=ttl_minutes)

        recovery_token = RecoveryToken(
            user_id=user.id,
            expires_at=expires_at,
        )

        saved_token = self._recovery_token_repository.save(recovery_token)
        return RecoveryResponseDto.from_domain(saved_token)

    def get_by_token(self, token: str) -> RecoveryResponseDto:
        recovery_token = self._recovery_token_repository.get_by_token(token)
        if recovery_token is None:
            raise RecoveryTokenNotFoundException(token)

        return RecoveryResponseDto.from_domain(recovery_token)

    def validate_token(self, token: str) -> RecoveryResponseDto:
        recovery_token = self._recovery_token_repository.get_by_token(token)
        if recovery_token is None:
            raise RecoveryTokenNotFoundException(token)

        if recovery_token.is_used:
            raise RecoveryTokenAlreadyUsedException()

        if recovery_token.is_expired():
            raise RecoveryTokenExpiredException()

        return RecoveryResponseDto.from_domain(recovery_token)

    def reset_password(self, dto: ResetPasswordWithTokenDto) -> None:
        recovery_token = self._recovery_token_repository.get_by_token(dto.token)
        if recovery_token is None:
            raise RecoveryTokenNotFoundException(dto.token)

        if recovery_token.is_used:
            raise RecoveryTokenAlreadyUsedException()

        if recovery_token.is_expired():
            raise RecoveryTokenExpiredException()

        self._user_service.reset_password(
            user_id=recovery_token.user_id,
            new_password=dto.new_password,
        )

        recovery_token.mark_as_used()
        self._recovery_token_repository.save(recovery_token)

    def list_by_user_id(self, user_id: UUID) -> list[RecoveryResponseDto]:
        tokens = self._recovery_token_repository.list_by_user_id(user_id)
        return [RecoveryResponseDto.from_domain(t) for t in tokens]
