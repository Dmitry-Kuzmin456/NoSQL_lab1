import threading
from uuid import UUID

from application.recovery.repository import IRecoveryTokenRepository
from domain.recovery_token import RecoveryToken


class InMemoryRecoveryTokenRepository(IRecoveryTokenRepository):
    def __init__(self) -> None:
        self._tokens: dict[str, RecoveryToken] = {}
        self._lock = threading.RLock()

    def save(self, recovery_token: RecoveryToken) -> RecoveryToken:
        with self._lock:
            self._tokens[recovery_token.token] = recovery_token
            return recovery_token

    def get_by_token(self, token: str) -> RecoveryToken | None:
        with self._lock:
            return self._tokens.get(token)

    def exists_by_token(self, token: str) -> bool:
        with self._lock:
            return token in self._tokens

    def mark_as_used(self, token: str) -> bool:
        with self._lock:
            rec_token = self._tokens.get(token)
            if rec_token is None:
                return False
            rec_token.mark_as_used()
            return True

    def list_by_user_id(self, user_id: UUID) -> list[RecoveryToken]:
        with self._lock:
            return [
                token for token in self._tokens.values() if token.user_id == user_id
            ]

    def delete(self, token: str) -> bool:
        with self._lock:
            if token in self._tokens:
                del self._tokens[token]
                return True
            return False

    def delete_all_for_user(self, user_id: UUID) -> int:
        with self._lock:
            keys_to_delete = [
                tok
                for tok, recovery_token in self._tokens.items()
                if recovery_token.user_id == user_id
            ]
            for tok in keys_to_delete:
                del self._tokens[tok]
            return len(keys_to_delete)

    def delete_expired(self) -> int:
        with self._lock:
            expired_keys = [
                tok for tok, token in self._tokens.items() if token.is_expired()
            ]
            for tok in expired_keys:
                del self._tokens[tok]
            return len(expired_keys)
