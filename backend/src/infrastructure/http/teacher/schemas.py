from uuid import UUID

from pydantic import BaseModel, Field

from application.teacher.dto import (
    AddProductToStudentsDto,
    BatchAddProductResultDto,
    TeacherResponseDto,
)
from domain.user import UserRole


class AddStudentRequest(BaseModel):
    student_id: UUID = Field(..., description="ID прикрепляемого ученика")


class AddProductToStudentsRequest(BaseModel):
    product_id: UUID = Field(..., description="ID рекомендуемого товара")
    note: str | None = Field(
        default=None,
        max_length=500,
        description="Заметка/рекомендация от преподавателя",
    )

    def to_dto(self) -> AddProductToStudentsDto:
        return AddProductToStudentsDto(
            product_id=self.product_id,
            note=self.note,
        )


class TeacherResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    student_ids: list[UUID]
    total_students: int

    @classmethod
    def from_dto(cls, dto: TeacherResponseDto) -> "TeacherResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            email=dto.email,
            role=dto.role,
            student_ids=dto.student_ids,
            total_students=dto.total_students,
        )


class BatchAddProductResponse(BaseModel):
    product_id: UUID
    affected_students: int
    student_ids: list[UUID]

    @classmethod
    def from_dto(cls, dto: BatchAddProductResultDto) -> "BatchAddProductResponse":
        return cls(
            product_id=dto.product_id,
            affected_students=dto.affected_students,
            student_ids=dto.student_ids,
        )
