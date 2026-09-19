from datetime import datetime
from typing import Any
from uuid import UUID

from application.session.repository import ISessionRepository
from domain.session import Session
from infrastructure.persistence.riak.client import (
    RiakClient,
    RiakObject,
    get_riak_client,
)


class RiakSessionRepository(ISessionRepository):
    """Репозиторий сессий для Riak KV."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "sessions",
        user_sessions_bucket: str = "user_sessions",
        bucket_type: str = "default",
        sets_bucket_type: str = "sets",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._user_sessions_bucket = user_sessions_bucket
        self._bucket_type = bucket_type
        self._sets_bucket_type = sets_bucket_type

    @staticmethod
    def _session_to_dict(session: Session) -> dict[str, Any]:
        return {
            "user_id": str(session.user_id),
            "refresh_token": session.refresh_token,
            "created_at": session.created_at.isoformat(),
            "expires_at": (
                session.expires_at.isoformat() if session.expires_at else None
            ),
        }

    @staticmethod
    def _dict_to_session(data: dict[str, Any]) -> Session:
        return Session(
            user_id=UUID(data["user_id"]),
            refresh_token=data["refresh_token"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
        )

    def save(self, session: Session) -> Session:
        """Сохранить сессию и добавить токен в CRDT множество пользователя."""
        obj = RiakObject(
            bucket=self._bucket,
            key=session.refresh_token,
            data=self._session_to_dict(session),
            bucket_type=self._bucket_type,
            vclock=None,
        )
        self._client.put(obj)

        self._client.set_add(
            bucket=self._user_sessions_bucket,
            key=str(session.user_id),
            elements=session.refresh_token,
            bucket_type=self._sets_bucket_type,
        )
        return session

    def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        """Получить сессию по refresh токену."""
        obj = self._client.get(
            bucket=self._bucket,
            key=refresh_token,
            bucket_type=self._bucket_type,
        )
        if obj is None or not isinstance(obj.data, dict):
            return None
        return self._dict_to_session(obj.data)

    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        """Получить список сессий пользователя."""
        tokens = self._client.set_get(
            bucket=self._user_sessions_bucket,
            key=str(user_id),
            bucket_type=self._sets_bucket_type,
        )
        sessions: list[Session] = []
        for token in tokens:
            session = self.get_by_refresh_token(token)
            if session is not None:
                sessions.append(session)
            else:
                self._client.set_remove(
                    bucket=self._user_sessions_bucket,
                    key=str(user_id),
                    elements=token,
                    bucket_type=self._sets_bucket_type,
                )
        return sessions

    def delete_by_refresh_token(self, refresh_token: str) -> bool:
        """Удалить сессию по refresh токену."""
        session = self.get_by_refresh_token(refresh_token)
        if session is None:
            return False

        deleted = self._client.delete(
            bucket=self._bucket,
            key=refresh_token,
            bucket_type=self._bucket_type,
        )
        self._client.set_remove(
            bucket=self._user_sessions_bucket,
            key=str(session.user_id),
            elements=refresh_token,
            bucket_type=self._sets_bucket_type,
        )
        return deleted

    def delete_all_for_user(self, user_id: UUID) -> int:
        """Удалить все сессии пользователя."""
        tokens = self._client.set_get(
            bucket=self._user_sessions_bucket,
            key=str(user_id),
            bucket_type=self._sets_bucket_type,
        )
        count = 0
        for token in tokens:
            if self._client.delete(
                bucket=self._bucket,
                key=token,
                bucket_type=self._bucket_type,
            ):
                count += 1
            self._client.set_remove(
                bucket=self._user_sessions_bucket,
                key=str(user_id),
                elements=token,
                bucket_type=self._sets_bucket_type,
            )
        return count
