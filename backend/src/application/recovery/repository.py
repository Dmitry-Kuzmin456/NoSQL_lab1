from abc import ABC, abstractmethod
from uuid import UUID

from domain.recovery_token import RecoveryToken


class IRecoveryTokenRepository(ABC):
    """Интерфейс токенов восстановления с поддержкой Secondary Index (2i)."""

    @abstractmethod
    def save(self, recovery_token: RecoveryToken) -> RecoveryToken:
        """Сохранить токен с установкой 2i индексов (user_id_bin, expires_at_int)."""
        raise NotImplementedError

    @abstractmethod
    def get_by_token(self, token: str) -> RecoveryToken | None:
        """Точечное O(1) чтение по первичному ключу token."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_token(self, token: str) -> bool:
        """Быстрая проверка существования через HEAD-запрос без выгрузки данных."""
        raise NotImplementedError

    @abstractmethod
    def mark_as_used(self, token: str) -> bool:
        """Точечное обновление статуса токена."""
        raise NotImplementedError

    @abstractmethod
    def find_tokens_by_user_id(self, user_id: UUID) -> list[RecoveryToken]:
        """Поиск токенов пользователя через вторичный индекс 2i user_id_bin."""
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[RecoveryToken]:
        """Получить все токены восстановления пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, token: str) -> bool:
        """Удалить токен по первичному ключу."""
        raise NotImplementedError

    @abstractmethod
    def delete_all_for_user(self, user_id: UUID) -> int:
        """Удалить все токены восстановления пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete_expired(self, current_timestamp: int | None = None) -> int:
        """Пакетное удаление протухших токенов по 2i диапазону expires_at_int <= current_timestamp."""
        raise NotImplementedError
