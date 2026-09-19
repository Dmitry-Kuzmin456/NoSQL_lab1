from datetime import datetime
from typing import Any
from uuid import UUID

from application.recovery.repository import IRecoveryTokenRepository
from domain.recovery_token import RecoveryToken
from infrastructure.persistence.riak.client import (
    RiakClient,
    RiakObject,
    get_riak_client,
)


class RiakRecoveryTokenRepository(IRecoveryTokenRepository):
    """Репозиторий токенов восстановления для Riak KV."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "recovery_tokens",
        bucket_type: str = "default",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._bucket_type = bucket_type

    @staticmethod
    def _token_to_dict(recovery_token: RecoveryToken) -> dict[str, Any]:
        return {
            "user_id": str(recovery_token.user_id),
            "token": recovery_token.token,
            "created_at": recovery_token.created_at.isoformat(),
            "expires_at": recovery_token.expires_at.isoformat(),
        }

    @staticmethod
    def _dict_to_token(data: dict[str, Any]) -> RecoveryToken:
        return RecoveryToken(
            user_id=UUID(data["user_id"]),
            token=data["token"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )

    def save(self, recovery_token: RecoveryToken) -> RecoveryToken:
        """Сохранить токен восстановления."""
        obj = RiakObject(
            bucket=self._bucket,
            key=recovery_token.token,
            data=self._token_to_dict(recovery_token),
            bucket_type=self._bucket_type,
            vclock=None,
        )
        self._client.put(obj)
        return recovery_token

    def get_by_token(self, token: str) -> RecoveryToken | None:
        """Получить токен восстановления по значению."""
        obj = self._client.get(
            bucket=self._bucket,
            key=token,
            bucket_type=self._bucket_type,
        )
        if obj is None or not isinstance(obj.data, dict):
            return None
        return self._dict_to_token(obj.data)

    def delete_by_token(self, token: str) -> bool:
        """Удалить токен восстановления."""
        return self._client.delete(
            bucket=self._bucket,
            key=token,
            bucket_type=self._bucket_type,
        )
