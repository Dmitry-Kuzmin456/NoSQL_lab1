from dataclasses import dataclass
from uuid import UUID

from domain.teacher import Teacher
from domain.user import UserRole


@dataclass(frozen=True)
class AddProductToStudentsDto:
    product_id: UUID
    note: str | None = None


@dataclass(frozen=True)
class BatchAddProductResultDto:
    product_id: UUID
    affected_students: int
    student_ids: list[UUID]


@dataclass(frozen=True)
class TeacherResponseDto:
    id: UUID
    name: str
    email: str
    role: UserRole
    student_ids: list[UUID]
    total_students: int

    @classmethod
    def from_domain(cls, teacher: Teacher) -> "TeacherResponseDto":
        student_list = sorted(teacher.student_ids)
        return cls(
            id=teacher.id,
            name=teacher.name,
            email=teacher.email,
            role=teacher.role,
            student_ids=student_list,
            total_students=len(student_list),
        )
