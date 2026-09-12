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
        email: str,
    ) -> str:
        """Create a signed access token (e.g. JWT) containing user claims."""
        ...

    @abstractmethod
    def verify_access_token(self, token: str) -> dict[str, Any]:
        """Verify and decode an access token, returning its payload claims."""
        ...
