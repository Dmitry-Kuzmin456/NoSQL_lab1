from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from application.teacher.repository import ITeacherRepository
from domain.teacher import Teacher
from domain.user import UserRole
from infrastructure.persistence.postgres.connection import get_postgres_pool


class PostgresTeacherRepository(ITeacherRepository):
    """Репозиторий преподавателей для PostgreSQL."""

    def __init__(self, pool: ConnectionPool | None = None) -> None:
        self._pool: ConnectionPool = pool or get_postgres_pool()

    def get_by_id(self, teacher_id: UUID) -> Teacher | None:
        with (
            self._pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            cur.execute(
                "SELECT id, name, email, password_hash, role FROM users WHERE id = %s AND role = %s",
                (teacher_id, UserRole.TEACHER.value),
            )
            user_row = cur.fetchone()
            if user_row is None:
                return None

            cur.execute(
                "SELECT student_id FROM teacher_students WHERE teacher_id = %s",
                (teacher_id,),
            )
            student_rows = cur.fetchall()
            student_ids = {row["student_id"] for row in student_rows}

            return Teacher(
                id=user_row["id"],
                name=user_row["name"],
                email=user_row["email"],
                password_hash=user_row["password_hash"],
                role=UserRole(user_row["role"]),
                student_ids=student_ids,
            )

    def exists_by_id(self, teacher_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM users WHERE id = %s AND role = %s",
                (teacher_id, UserRole.TEACHER.value),
            )
            return cur.fetchone() is not None

    def assign_student(self, teacher_id: UUID, student_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                    INSERT INTO teacher_students (teacher_id, student_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                (teacher_id, student_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def unassign_student(self, teacher_id: UUID, student_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM teacher_students WHERE teacher_id = %s AND student_id = %s",
                (teacher_id, student_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def save(self, teacher: Teacher) -> Teacher:
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
                (
                    teacher.id,
                    teacher.name,
                    teacher.email,
                    teacher.password_hash,
                    UserRole.TEACHER.value,
                ),
            )
            cur.execute(
                "DELETE FROM teacher_students WHERE teacher_id = %s",
                (teacher.id,),
            )
            if teacher.student_ids:
                cur.executemany(
                    "INSERT INTO teacher_students (teacher_id, student_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    [(teacher.id, sid) for sid in teacher.student_ids],
                )
            conn.commit()
            return teacher

    def delete(self, teacher_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE id = %s AND role = %s",
                (teacher_id, UserRole.TEACHER.value),
            )
            conn.commit()
            return cur.rowcount > 0
