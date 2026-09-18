from uuid import UUID

from application.teacher.repository import ITeacherRepository
from domain.teacher import Teacher


class PostgresTeacherRepository(ITeacherRepository):
    """Реализация репозитория преподавателей для PostgreSQL."""

    def get_by_id(self, teacher_id: UUID) -> Teacher | None:
        raise NotImplementedError

    def exists_by_id(self, teacher_id: UUID) -> bool:
        raise NotImplementedError

    def assign_student(self, teacher_id: UUID, student_id: UUID) -> bool:
        raise NotImplementedError

    def unassign_student(self, teacher_id: UUID, student_id: UUID) -> bool:
        raise NotImplementedError

    def save(self, teacher: Teacher) -> Teacher:
        raise NotImplementedError

    def delete(self, teacher_id: UUID) -> bool:
        raise NotImplementedError
