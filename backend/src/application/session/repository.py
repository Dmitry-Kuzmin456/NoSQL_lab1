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
    def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        """Точечное чтение сессии O(1) по первичному ключу refresh_token."""
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        """Получить все сессии пользователя через 2i индекс user_id_bin."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_refresh_token(self, refresh_token: str) -> bool:
        """Удалить сессию по ключу refresh_token."""
        raise NotImplementedError

    @abstractmethod
    def delete_all_for_user(self, user_id: UUID) -> int:
        """Удалить все сессии пользователя."""
        raise NotImplementedError
