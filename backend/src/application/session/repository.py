from abc import ABC, abstractmethod
from uuid import UUID

from domain.session import Session


class ISessionRepository(ABC):
    @abstractmethod
    def save(self, session: Session) -> Session:
        """Сохранить или обновить сессию."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, session_id: UUID) -> Session | None:
        """Получить сессию по ID."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, session_id: UUID) -> bool:
        """Проверить существование сессии по ID без загрузки тела."""
        raise NotImplementedError

    @abstractmethod
    def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        """Получить сессию по refresh токену."""
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        """Получить все сессии пользователя."""
        raise NotImplementedError

    @abstractmethod
    def revoke(self, session_id: UUID) -> bool:
        """Отозвать сессию по ID."""
        raise NotImplementedError

    @abstractmethod
    def revoke_by_refresh_token(self, refresh_token: str) -> bool:
        """Отозвать сессию по refresh токену без предварительной загрузки объекта."""
        raise NotImplementedError

    @abstractmethod
    def revoke_all_for_user(self, user_id: UUID) -> int:
        """Пакетно отозвать все сессии пользователя."""
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
    def delete_expired(self) -> int:
        """Очистить протухшие сессии (application-level expiration). Возвращает количество удаленных."""
        raise NotImplementedError
