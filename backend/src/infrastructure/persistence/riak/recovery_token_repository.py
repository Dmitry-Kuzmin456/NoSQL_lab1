from uuid import UUID

from application.recovery.repository import IRecoveryTokenRepository
from domain.recovery_token import RecoveryToken


class RiakRecoveryTokenRepository(IRecoveryTokenRepository):
    """Реализация репозитория токенов восстановления на базе Riak KV + 2i Secondary Index."""

    def save(self, recovery_token: RecoveryToken) -> RecoveryToken:
        raise NotImplementedError

    def get_by_token(self, token: str) -> RecoveryToken | None:
        raise NotImplementedError

    def exists_by_token(self, token: str) -> bool:
        raise NotImplementedError

    def mark_as_used(self, token: str) -> bool:
        raise NotImplementedError

    def find_tokens_by_user_id(self, user_id: UUID) -> list[RecoveryToken]:
        raise NotImplementedError

    def list_by_user_id(self, user_id: UUID) -> list[RecoveryToken]:
        raise NotImplementedError

    def delete(self, token: str) -> bool:
        raise NotImplementedError

    def delete_all_for_user(self, user_id: UUID) -> int:
        raise NotImplementedError

    def delete_expired(self, current_timestamp: int | None = None) -> int:
        raise NotImplementedError
