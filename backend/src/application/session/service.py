import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from domain.session import Session

from .dto import SessionResponseDto
from .exceptions import (
    SessionExpiredException,
    SessionNotFoundException,
    SessionRevokedException,
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

        if session.is_revoked:
            raise SessionRevokedException()

        if session.is_expired():
            raise SessionExpiredException()

        new_refresh_token = secrets.token_urlsafe(64)
        new_expires_at = datetime.now(UTC) + timedelta(days=ttl_days)
        session.rotate_refresh_token(new_refresh_token, new_expires_at)

        saved_session = self._session_repository.save(session)
        return SessionResponseDto.from_domain(saved_session)

    def get_by_id(self, session_id: UUID) -> SessionResponseDto:
        session = self._session_repository.get_by_id(session_id)
        if session is None:
            raise SessionNotFoundException(session_id)

        if session.is_revoked:
            raise SessionRevokedException()

        if session.is_expired():
            raise SessionExpiredException()

        return SessionResponseDto.from_domain(session)

    def get_by_refresh_token(self, refresh_token: str) -> SessionResponseDto:
        session = self._session_repository.get_by_refresh_token(refresh_token)
        if session is None:
            raise SessionNotFoundException(refresh_token)

        if session.is_revoked:
            raise SessionRevokedException()

        if session.is_expired():
            raise SessionExpiredException()

        return SessionResponseDto.from_domain(session)

    def revoke_session(self, session_id: UUID) -> None:
        session = self._session_repository.get_by_id(session_id)
        if session is None:
            raise SessionNotFoundException(session_id)

        session.revoke()
        self._session_repository.save(session)

    def revoke_all_user_sessions(self, user_id: UUID) -> int:
        sessions = self._session_repository.list_by_user_id(user_id)
        count = 0
        for s in sessions:
            if not s.is_revoked:
                s.revoke()
                self._session_repository.save(s)
                count += 1
        return count

    def get_user_sessions(self, user_id: UUID) -> list[SessionResponseDto]:
        sessions = self._session_repository.list_by_user_id(user_id)
        return [
            SessionResponseDto.from_domain(s)
            for s in sessions
            if not s.is_expired() and not s.is_revoked
        ]
