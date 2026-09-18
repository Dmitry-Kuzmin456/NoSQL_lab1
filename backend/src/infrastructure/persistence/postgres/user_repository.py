from uuid import UUID

from application.user.repository import IUserRepository
from domain.user import User


class PostgresUserRepository(IUserRepository):
    """Реализация репозитория пользователей для PostgreSQL (System of Record)."""

    def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    def exists_by_id(self, user_id: UUID) -> bool:
        raise NotImplementedError

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    def exists_by_email(self, email: str) -> bool:
        raise NotImplementedError

    def update_password_hash(self, user_id: UUID, new_password_hash: str) -> bool:
        raise NotImplementedError

    def save(self, user: User) -> User:
        raise NotImplementedError

    def delete(self, user_id: UUID) -> bool:
        raise NotImplementedError
