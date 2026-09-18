from application.recovery.repository import IRecoveryTokenRepository
from domain.recovery_token import RecoveryToken


class RiakRecoveryTokenRepository(IRecoveryTokenRepository):
    """Репозиторий токенов восстановления для Riak KV."""

    def save(self, recovery_token: RecoveryToken) -> RecoveryToken:
        raise NotImplementedError

    def get_by_token(self, token: str) -> RecoveryToken | None:
        raise NotImplementedError

    def delete_by_token(self, token: str) -> bool:
        raise NotImplementedError
