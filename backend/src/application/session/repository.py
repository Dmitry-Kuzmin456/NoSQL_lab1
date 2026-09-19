from abc import ABC, abstractmethod
from uuid import UUID

from domain.session import Session


class ISessionRepository(ABC):
    """Интерфейс репозитория сессий."""

    @abstractmethod
    def save(self, session: Session) -> Session:
        """Сохранить сессию."""
        raise NotImplementedError

    @abstractmethod
    def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        """Получить сессию по refresh токену."""
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        """Получить список сессий пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_refresh_token(
        self, refresh_token: str, user_id: UUID | None = None
    ) -> bool:
        """Удалить сессию по refresh токену."""
        raise NotImplementedError

    @abstractmethod
    def delete_all_for_user(self, user_id: UUID) -> int:
        """Удалить все сессии пользователя."""
        raise NotImplementedError
