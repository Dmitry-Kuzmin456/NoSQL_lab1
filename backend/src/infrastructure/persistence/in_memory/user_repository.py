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

    def get_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        with self._lock:
            for user in self._users.values():
                if user.email.strip().lower() == normalized_email:
                    return user
            return None

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
