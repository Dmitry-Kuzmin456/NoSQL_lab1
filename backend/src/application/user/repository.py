from abc import ABC, abstractmethod
from uuid import UUID

from domain.user import User


class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по UUID."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, user_id: UUID) -> bool:
        """Проверить существование пользователя по UUID без загрузки объекта."""
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Проверить занятость email без вычитки сущности пользователя."""
        raise NotImplementedError

    @abstractmethod
    def update_password_hash(self, user_id: UUID, new_password_hash: str) -> bool:
        """Обновить хеш пароля пользователя."""
        raise NotImplementedError

    @abstractmethod
    def save(self, user: User) -> User:
        """Сохранить или обновить пользователя."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        """Удалить пользователя по UUID."""
        raise NotImplementedError
