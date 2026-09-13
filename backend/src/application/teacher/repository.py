from abc import ABC, abstractmethod
from uuid import UUID

from domain.teacher import Teacher


class ITeacherRepository(ABC):
    @abstractmethod
    def get_by_id(self, teacher_id: UUID) -> Teacher | None:
        """Получить преподавателя по UUID."""
        raise NotImplementedError

    @abstractmethod
    def save(self, teacher: Teacher) -> Teacher:
        """Сохранить или обновить преподавателя."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, teacher_id: UUID) -> bool:
        """Удалить преподавателя по UUID."""
        raise NotImplementedError
