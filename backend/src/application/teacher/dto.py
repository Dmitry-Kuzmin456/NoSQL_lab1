from dataclasses import dataclass, field
from uuid import UUID

from application.user.dto import UserResponseDto
from domain.teacher import Teacher
from domain.user import UserRole


@dataclass(frozen=True)
class AddProductToStudentsDto:
    product_id: UUID


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
    students: list[UserResponseDto] = field(default_factory=list)

    @classmethod
    def from_domain(
        cls,
        teacher: Teacher,
        students: list[UserResponseDto] | None = None,
    ) -> "TeacherResponseDto":
        student_list = sorted(teacher.student_ids)
        return cls(
            id=teacher.id,
            name=teacher.name,
            email=teacher.email,
            role=teacher.role,
            student_ids=student_list,
            total_students=len(student_list),
            students=students if students is not None else [],
        )
