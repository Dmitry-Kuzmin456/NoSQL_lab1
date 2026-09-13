import threading
from uuid import UUID

from application.session import ISessionRepository
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
