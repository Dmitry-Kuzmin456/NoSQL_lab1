from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from application.user.repository import IUserRepository
from domain.user import User, UserRole
from infrastructure.persistence.postgres.connection import get_postgres_pool


class PostgresUserRepository(IUserRepository):
    """Репозиторий пользователей для PostgreSQL."""

    def __init__(self, pool: ConnectionPool | None = None) -> None:
        self._pool: ConnectionPool = pool or get_postgres_pool()

    def get_by_id(self, user_id: UUID) -> User | None:
        with (
            self._pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            cur.execute(
                "SELECT id, name, email, password_hash, role FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return User(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                password_hash=row["password_hash"],
                role=UserRole(row["role"]),
            )

    def exists_by_id(self, user_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM users WHERE id = %s",
                (user_id,),
            )
            return cur.fetchone() is not None

    def get_by_email(self, email: str) -> User | None:
        with (
            self._pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            cur.execute(
                "SELECT id, name, email, password_hash, role FROM users WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return User(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                password_hash=row["password_hash"],
                role=UserRole(row["role"]),
            )

    def exists_by_email(self, email: str) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM users WHERE email = %s",
                (email,),
            )
            return cur.fetchone() is not None

    def update_password_hash(self, user_id: UUID, new_password_hash: str) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_password_hash, user_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def save(self, user: User) -> User:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (id, name, email, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    password_hash = EXCLUDED.password_hash,
                    role = EXCLUDED.role
                """,
                (user.id, user.name, user.email, user.password_hash, user.role.value),
            )
            conn.commit()
            return user

    def delete(self, user_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,),
            )
            conn.commit()
            return cur.rowcount > 0
