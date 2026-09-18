from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from domain.user import UserRole


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(
        self,
        user_id: UUID,
        role: UserRole,
    ) -> str:
        """Создать токен доступа."""
        ...

    @abstractmethod
    def verify_access_token(self, token: str) -> dict[str, Any]:
        """Проверить токен доступа."""
        ...
