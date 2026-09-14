import threading
from uuid import UUID

from application.user.repository import IUserRepository
from domain.user import User


class InMemoryUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}
        self._lock = threading.RLock()

    def get_by_id(self, user_id: UUID) -> User | None:
        with self._lock:
            return self._users.get(user_id)

    def exists_by_id(self, user_id: UUID) -> bool:
        with self._lock:
            return user_id in self._users

    def get_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        with self._lock:
            for user in self._users.values():
                if user.email.strip().lower() == normalized_email:
                    return user
            return None

    def exists_by_email(self, email: str) -> bool:
        normalized_email = email.strip().lower()
        with self._lock:
            return any(
                u.email.strip().lower() == normalized_email
                for u in self._users.values()
            )

    def update_password_hash(self, user_id: UUID, new_password_hash: str) -> bool:
        with self._lock:
            user = self._users.get(user_id)
            if user is None:
                return False
            user.password_hash = new_password_hash
            return True

    def save(self, user: User) -> User:
        with self._lock:
            self._users[user.id] = user
            return user

    def delete(self, user_id: UUID) -> bool:
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]
                return True
            return False
