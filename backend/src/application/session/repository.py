from abc import ABC, abstractmethod
from uuid import UUID

from domain.session import Session


class ISessionRepository(ABC):
    """Интерфейс сессий и токенов авторизации на базе Riak KV + 2i."""

    @abstractmethod
    def save(self, session: Session) -> Session:
        """Сохранить или обновить сессию с индексацией user_id_bin и expires_at_int."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, session_id: UUID) -> Session | None:
        """Получить сессию по ID."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, session_id: UUID) -> bool:
        """Проверить существование сессии по ID без загрузки тела (HEAD)."""
        raise NotImplementedError

    @abstractmethod
    def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        """Точечное чтение сессии O(1) по первичному ключу refresh_token."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_refresh_token(self, refresh_token: str) -> bool:
        """Быстрая проверка валидности сессии через HEAD-запрос."""
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        """Получить все сессии пользователя через 2i индекс user_id_bin."""
        raise NotImplementedError

    @abstractmethod
    def revoke(self, session_id: UUID) -> bool:
        """Отозвать сессию по ID."""
        raise NotImplementedError

    @abstractmethod
    def revoke_by_refresh_token(self, refresh_token: str) -> bool:
        """Отозвать сессию по ключу refresh_token без предварительной загрузки объекта."""
        raise NotImplementedError

    @abstractmethod
    def revoke_all_for_user(self, user_id: UUID) -> int:
        """Пакетный отзыв всех сессий пользователя через 2i поиск + параллельное удаление/обновление."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, session_id: UUID) -> bool:
        """Удалить сессию по ID."""
        raise NotImplementedError

    @abstractmethod
    def delete_all_for_user(self, user_id: UUID) -> int:
        """Удалить все сессии пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete_expired(self, current_timestamp: int | None = None) -> int:
        """Очистить просроченные сессии через диапазонный 2i запрос expires_at_int <= current_timestamp."""
        raise NotImplementedError
