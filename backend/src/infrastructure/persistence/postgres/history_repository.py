import json
from typing import Any
from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from domain.history import OperationEvent, OperationType
from infrastructure.persistence.postgres.connection import get_postgres_pool


class PostgresHistoryRepository:
    """Репозиторий истории операций для PostgreSQL."""

    def __init__(self, pool: ConnectionPool | None = None) -> None:
        self._pool: ConnectionPool = pool or get_postgres_pool()

    @staticmethod
    def _row_to_event(row: dict[str, Any]) -> OperationEvent:
        return OperationEvent(
            id=row["id"],
            user_id=row["user_id"],
            action=OperationType(row["action"]),
            target_id=row["target_id"],
            details=row["details"]
            if isinstance(row["details"], dict)
            else json.loads(row["details"] or "{}"),
            timestamp=row["timestamp"],
        )

    def save(self, event: OperationEvent) -> None:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO operation_history (id, user_id, action, target_id, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    action = EXCLUDED.action,
                    target_id = EXCLUDED.target_id,
                    details = EXCLUDED.details,
                    timestamp = EXCLUDED.timestamp
                """,
                (
                    event.id,
                    event.user_id,
                    event.action.value,
                    event.target_id,
                    json.dumps(event.details),
                    event.timestamp,
                ),
            )
            conn.commit()

    def list_by_user_id(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[OperationEvent]:
        with self._pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, user_id, action, target_id, details, timestamp
                FROM operation_history
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, offset),
            )
            rows = cur.fetchall()
            return [self._row_to_event(r) for r in rows]

    def count_by_user_id(self, user_id: UUID) -> int:
        with self._pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT count(*) as count FROM operation_history WHERE user_id = %s",
                (user_id,),
            )
            return int((cur.fetchone() or {}).get("count", 0))

    def delete_by_user_id(self, user_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM operation_history WHERE user_id = %s", (user_id,))
            conn.commit()
            return cur.rowcount > 0
