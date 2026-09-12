from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from application.auth.token import ITokenService
from domain.user import UserRole


class JwtTokenService(ITokenService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expire_minutes: int = 15,
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(
        self,
        user_id: UUID,
        role: UserRole,
    ) -> str:
        now = datetime.now(UTC)
        expire = now + timedelta(minutes=self._expire_minutes)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "role": str(role.value),
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_access_token(self, token: str) -> dict[str, Any]:
        payload: dict[str, Any] = jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
        )
        return payload
