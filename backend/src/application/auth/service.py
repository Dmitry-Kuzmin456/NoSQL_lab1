from uuid import UUID

from application.session.service import SessionService
from application.user.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
)
from application.user.hasher import IPasswordHasher
from application.user.service import UserService

from .dto import AuthResponseDto, LoginDto
from .token import ITokenService


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        session_service: SessionService,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ):
        self._user_service = user_service
        self._session_service = session_service
        self._password_hasher = password_hasher
        self._token_service = token_service

    def login(self, dto: LoginDto, ttl_days: int = 30) -> AuthResponseDto:
        try:
            user = self._user_service.get_by_email(dto.email)
        except UserNotFoundException:
            raise InvalidCredentialsException()

        if not self._password_hasher.verify(dto.password, user.password_hash):
            raise InvalidCredentialsException()

        session_dto = self._session_service.create_session(
            user_id=user.id,
            ttl_days=ttl_days,
        )

        access_token = self._token_service.create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
        )

        return AuthResponseDto(
            user=user.to_response_dto(),
            session=session_dto,
            access_token=access_token,
        )

    def refresh(self, refresh_token: str, ttl_days: int = 30) -> AuthResponseDto:
        session_dto = self._session_service.refresh_session(
            refresh_token=refresh_token,
            ttl_days=ttl_days,
        )
        user_dto = self._user_service.get_by_id(session_dto.user_id)
        access_token = self._token_service.create_access_token(
            user_id=user_dto.id,
            role=user_dto.role,
            email=user_dto.email,
        )

        return AuthResponseDto(
            user=user_dto,
            session=session_dto,
            access_token=access_token,
        )

    def logout(self, session_id: UUID) -> None:
        self._session_service.revoke_session(session_id)

    def logout_by_refresh_token(self, refresh_token: str) -> None:
        session_dto = self._session_service.get_by_refresh_token(refresh_token)
        self._session_service.revoke_session(session_dto.id)

    def logout_all(self, user_id: UUID) -> int:
        return self._session_service.revoke_all_user_sessions(user_id)
