from abc import ABC, abstractmethod

from domain.recovery_token import RecoveryToken


class IRecoveryTokenRepository(ABC):
    """Интерфейс токенов восстановления на базе Riak KV (Bucket: 'recovery_tokens', Key: token)."""

    @abstractmethod
    def save(self, recovery_token: RecoveryToken) -> RecoveryToken:
        """Сохранить токен восстановления."""
        raise NotImplementedError

    @abstractmethod
    def get_by_token(self, token: str) -> RecoveryToken | None:
        """Получить токен восстановления по значению (O(1))."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_token(self, token: str) -> bool:
        """Удалить токен восстановления по значению."""
        raise NotImplementedError
