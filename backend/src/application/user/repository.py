from abc import ABC, abstractmethod
from uuid import UUID

from domain.user import User, UserRole


class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по UUID."""
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        raise NotImplementedError

    @abstractmethod
    def save(self, user: User) -> User:
        """Сохранить или обновить пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        """Удалить пользователя по UUID."""
        raise NotImplementedError
