from dataclasses import dataclass, field
from uuid import UUID

from domain.user import User


@dataclass
class Teacher(User):
    student_ids: set[UUID] = field(default_factory=set)

    def add_student(self, student_id: UUID) -> None:
        if student_id == self.id:
            raise ValueError("Учитель не может добавить сам себя в список своих учеников.")
        self.student_ids.add(student_id)

    def remove_student(self, student_id: UUID) -> None:
        self.student_ids.discard(student_id)

    def has_student(self, student_id: UUID) -> bool:
        return student_id in self.student_ids

    def get_student_ids(self) -> list[UUID]:
        return list(self.student_ids)
