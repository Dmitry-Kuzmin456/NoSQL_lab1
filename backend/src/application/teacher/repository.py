from abc import ABC, abstractmethod
from uuid import UUID

from domain.teacher import Teacher
from domain.user import User


class ITeacherRepository(ABC):
    """Интерфейс репозитория преподавателей."""

    @abstractmethod
    def get_by_id(self, teacher_id: UUID) -> Teacher | None:
        """Получить преподавателя по ID."""
        raise NotImplementedError

    @abstractmethod
    def get_students(self, teacher_id: UUID) -> list[User]:
        """Получить список прикрепленных студентов преподавателя одним запросом."""
        raise NotImplementedError

    @abstractmethod
    def exists_by_id(self, teacher_id: UUID) -> bool:
        """Проверить существование преподавателя."""
        raise NotImplementedError

    @abstractmethod
    def assign_student(self, teacher_id: UUID, student_id: UUID) -> bool:
        """Прикрепить студента к преподавателю."""
        raise NotImplementedError

    @abstractmethod
    def unassign_student(self, teacher_id: UUID, student_id: UUID) -> bool:
        """Открепить студента от преподавателя."""
        raise NotImplementedError

    @abstractmethod
    def save(self, teacher: Teacher) -> Teacher:
        """Сохранить преподавателя."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, teacher_id: UUID) -> bool:
        """Удалить преподавателя."""
        raise NotImplementedError
