import copy
import threading
from uuid import UUID

from application.teacher.repository import ITeacherRepository
from application.user.repository import IUserRepository
from domain.teacher import Teacher
from domain.user import UserRole


class InMemoryTeacherRepository(ITeacherRepository):
    """Репозиторий учителей, инкапсулирующий и расширяющий IUserRepository."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository
        self._student_assignments: dict[UUID, set[UUID]] = {}
        self._lock = threading.RLock()

    def get_by_id(self, teacher_id: UUID) -> Teacher | None:
        user = self._user_repository.get_by_id(teacher_id)
        if user is None or user.role != UserRole.TEACHER:
            return None

        with self._lock:
            student_ids = copy.deepcopy(
                self._student_assignments.get(teacher_id, set())
            )

        return Teacher(
            id=user.id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            student_ids=student_ids,
        )

    def save(self, teacher: Teacher) -> Teacher:
        self._user_repository.save(teacher)

        with self._lock:
            self._student_assignments[teacher.id] = copy.deepcopy(teacher.student_ids)

        return copy.deepcopy(teacher)

    def delete(self, teacher_id: UUID) -> bool:
        with self._lock:
            self._student_assignments.pop(teacher_id, None)

        return self._user_repository.delete(teacher_id)
