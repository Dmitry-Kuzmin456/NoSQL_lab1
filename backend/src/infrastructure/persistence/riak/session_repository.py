from uuid import UUID

from application.session.repository import ISessionRepository
from domain.session import Session


class RiakSessionRepository(ISessionRepository):
    """Реализация репозитория сессий и refresh токенов на базе Riak KV + 2i Secondary Index."""

    def save(self, session: Session) -> Session:
        raise NotImplementedError

    def get_by_id(self, session_id: UUID) -> Session | None:
        raise NotImplementedError

    def exists_by_id(self, session_id: UUID) -> bool:
        raise NotImplementedError

    def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        raise NotImplementedError

    def exists_by_refresh_token(self, refresh_token: str) -> bool:
        raise NotImplementedError

    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        raise NotImplementedError

    def revoke(self, session_id: UUID) -> bool:
        raise NotImplementedError

    def revoke_by_refresh_token(self, refresh_token: str) -> bool:
        raise NotImplementedError

    def revoke_all_for_user(self, user_id: UUID) -> int:
        raise NotImplementedError

    def delete(self, session_id: UUID) -> bool:
        raise NotImplementedError

    def delete_all_for_user(self, user_id: UUID) -> int:
        raise NotImplementedError

    def delete_expired(self, current_timestamp: int | None = None) -> int:
        raise NotImplementedError
