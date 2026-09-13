from uuid import UUID

from fastapi import APIRouter, status

from infrastructure.http.user.schemas import UserResponse

from .dependencies import TeacherServiceDep
from .schemas import (
    AddProductToStudentsRequest,
    AddStudentRequest,
    BatchAddProductResponse,
    TeacherResponse,
)

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get(
    "/{teacher_id}",
    response_model=TeacherResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить профиль преподавателя со списком ID учеников",
)
def get_teacher_profile(
    teacher_id: UUID,
    service: TeacherServiceDep,
) -> TeacherResponse:
    dto = service.get_teacher(teacher_id)
    return TeacherResponse.from_dto(dto)


@router.get(
    "/{teacher_id}/students",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить подробный список учеников преподавателя",
)
def get_students(
    teacher_id: UUID,
    service: TeacherServiceDep,
) -> list[UserResponse]:
    students = service.get_students(teacher_id)
    return [UserResponse.from_dto(s) for s in students]


@router.post(
    "/{teacher_id}/students",
    response_model=TeacherResponse,
    status_code=status.HTTP_200_OK,
    summary="Прикрепить ученика к преподавателю",
)
def add_student(
    teacher_id: UUID,
    request: AddStudentRequest,
    service: TeacherServiceDep,
) -> TeacherResponse:
    dto = service.add_student(
        teacher_id=teacher_id,
        student_id=request.student_id,
    )
    return TeacherResponse.from_dto(dto)


@router.delete(
    "/{teacher_id}/students/{student_id}",
    response_model=TeacherResponse,
    status_code=status.HTTP_200_OK,
    summary="Открепить ученика от преподавателя",
)
def remove_student(
    teacher_id: UUID,
    student_id: UUID,
    service: TeacherServiceDep,
) -> TeacherResponse:
    dto = service.remove_student(
        teacher_id=teacher_id,
        student_id=student_id,
    )
    return TeacherResponse.from_dto(dto)


@router.post(
    "/{teacher_id}/students/favourites",
    response_model=BatchAddProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Добавить товар в избранное всем ученикам преподавателя",
)
def add_product_to_all_students(
    teacher_id: UUID,
    request: AddProductToStudentsRequest,
    service: TeacherServiceDep,
) -> BatchAddProductResponse:
    dto = service.add_product_to_all_students(
        teacher_id=teacher_id,
        dto=request.to_dto(),
    )
    return BatchAddProductResponse.from_dto(dto)
