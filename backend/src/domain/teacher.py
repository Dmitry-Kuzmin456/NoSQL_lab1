from dataclasses import dataclass, field
from uuid import UUID

from domain.user import User


@dataclass
class Teacher(User):
    student_ids: set[UUID] = field(default_factory=set)

    def has_student(self, student_id: UUID) -> bool:
        return student_id in self.student_ids

    def get_student_ids(self) -> list[UUID]:
        return list(self.student_ids)
