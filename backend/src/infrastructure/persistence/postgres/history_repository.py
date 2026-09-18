from uuid import UUID

from domain.history import OperationEvent


class PostgresHistoryRepository:
    """Реализация постоянного реляционного хранилища истории операций для PostgreSQL."""

    def save(self, event: OperationEvent) -> None:
        raise NotImplementedError

    def list_by_user_id(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[OperationEvent], int]:
        raise NotImplementedError

    def count_by_user_id(self, user_id: UUID) -> int:
        raise NotImplementedError

    def delete_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError
