from abc import ABC, abstractmethod
from uuid import UUID

from domain.recovery_token import RecoveryToken


class IRecoveryTokenRepository(ABC):
    @abstractmethod
    def save(self, recovery_token: RecoveryToken) -> RecoveryToken:
        """Сохранить или обновить токен восстановления."""
        raise NotImplementedError

    @abstractmethod
    def get_by_token(self, token: str) -> RecoveryToken | None:
        """Получить токен восстановления по значению."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_token(self, token: str) -> bool:
        """Проверить существование токена без выгрузки данных."""
        raise NotImplementedError

    @abstractmethod
    def mark_as_used(self, token: str) -> bool:
        """Пометить токен восстановления как использованный."""
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[RecoveryToken]:
        """Получить все токены восстановления пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, token: str) -> bool:
        """Удалить токен восстановления."""
        raise NotImplementedError

    @abstractmethod
    def delete_all_for_user(self, user_id: UUID) -> int:
        """Удалить все токены восстановления пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete_expired(self) -> int:
        """Очистить истекшие токены восстановления (TTL / application-level cleanup)."""
        raise NotImplementedError
