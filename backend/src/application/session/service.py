import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from domain.session import Session

from .dto import SessionResponseDto
from .exceptions import (
    SessionExpiredException,
    SessionNotFoundException,
)
from .repository import ISessionRepository


class SessionService:
    def __init__(self, session_repository: ISessionRepository):
        self._session_repository = session_repository

    def create_session(self, user_id: UUID, ttl_days: int = 30) -> SessionResponseDto:
        refresh_token = secrets.token_urlsafe(64)
        expires_at = datetime.now(UTC) + timedelta(days=ttl_days)

        session = Session(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )

        saved_session = self._session_repository.save(session)
        return SessionResponseDto.from_domain(saved_session)

    def refresh_session(
        self, refresh_token: str, ttl_days: int = 30
    ) -> SessionResponseDto:
        session = self._session_repository.get_by_refresh_token(refresh_token)
        if session is None:
            raise SessionNotFoundException(refresh_token)

        if session.is_expired():
            self._session_repository.delete_by_refresh_token(refresh_token)
            raise SessionExpiredException()

        self._session_repository.delete_by_refresh_token(refresh_token)

        new_refresh_token = secrets.token_urlsafe(64)
        new_expires_at = datetime.now(UTC) + timedelta(days=ttl_days)
        new_session = Session(
            user_id=session.user_id,
            refresh_token=new_refresh_token,
            expires_at=new_expires_at,
        )

        saved_session = self._session_repository.save(new_session)
        return SessionResponseDto.from_domain(saved_session)

    def get_by_refresh_token(self, refresh_token: str) -> SessionResponseDto:
        session = self._session_repository.get_by_refresh_token(refresh_token)
        if session is None:
            raise SessionNotFoundException(refresh_token)

        if session.is_expired():
            raise SessionExpiredException()

        return SessionResponseDto.from_domain(session)

    def delete_by_refresh_token(self, refresh_token: str) -> None:
        if not self._session_repository.delete_by_refresh_token(refresh_token):
            raise SessionNotFoundException(refresh_token)

    def delete_all_user_sessions(self, user_id: UUID) -> int:
        return self._session_repository.delete_all_for_user(user_id)

    def get_user_sessions(self, user_id: UUID) -> list[SessionResponseDto]:
        sessions = self._session_repository.list_by_user_id(user_id)
        return [
            SessionResponseDto.from_domain(s)
            for s in sessions
            if not s.is_expired()
        ]
