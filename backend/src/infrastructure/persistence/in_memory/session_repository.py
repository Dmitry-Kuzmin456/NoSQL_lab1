import threading
from uuid import UUID

from application.session.repository import ISessionRepository
from domain.session import Session


class InMemorySessionRepository(ISessionRepository):
    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}
        self._lock = threading.RLock()

    def save(self, session: Session) -> Session:
        with self._lock:
            self._sessions[session.id] = session
            return session

    def get_by_id(self, session_id: UUID) -> Session | None:
        with self._lock:
            return self._sessions.get(session_id)

    def exists_by_id(self, session_id: UUID) -> bool:
        with self._lock:
            return session_id in self._sessions

    def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        with self._lock:
            for session in self._sessions.values():
                if session.refresh_token == refresh_token:
                    return session
            return None

    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        with self._lock:
            return [
                session
                for session in self._sessions.values()
                if session.user_id == user_id
            ]

    def revoke(self, session_id: UUID) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            session.is_revoked = True
            return True

    def revoke_by_refresh_token(self, refresh_token: str) -> bool:
        with self._lock:
            for session in self._sessions.values():
                if session.refresh_token == refresh_token:
                    session.is_revoked = True
                    return True
            return False

    def revoke_all_for_user(self, user_id: UUID) -> int:
        with self._lock:
            count = 0
            for session in self._sessions.values():
                if session.user_id == user_id and not session.is_revoked:
                    session.is_revoked = True
                    count += 1
            return count

    def delete(self, session_id: UUID) -> bool:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def delete_all_for_user(self, user_id: UUID) -> int:
        with self._lock:
            ids_to_delete = [
                sid
                for sid, session in self._sessions.items()
                if session.user_id == user_id
            ]
            for sid in ids_to_delete:
                del self._sessions[sid]
            return len(ids_to_delete)

    def delete_expired(self) -> int:
        with self._lock:
            expired_ids = [
                sid for sid, session in self._sessions.items() if session.is_expired()
            ]
            for sid in expired_ids:
                del self._sessions[sid]
            return len(expired_ids)
