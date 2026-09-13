from uuid import UUID

from fastapi import APIRouter, status

from infrastructure.http.middleware.authentication_middleware import CurrentUserDep
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
    "/me",
    response_model=TeacherResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить профиль текущего преподавателя со списком ID учеников",
)
def get_my_teacher_profile(
    current_user: CurrentUserDep,
    service: TeacherServiceDep,
) -> TeacherResponse:
    dto = service.get_teacher(current_user.id)
    return TeacherResponse.from_dto(dto)


@router.get(
    "/me/students",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить подробный список учеников текущего преподавателя",
)
def get_my_students(
    current_user: CurrentUserDep,
    service: TeacherServiceDep,
) -> list[UserResponse]:
    students = service.get_students(current_user.id)
    return [UserResponse.from_dto(s) for s in students]


@router.post(
    "/me/students",
    response_model=TeacherResponse,
    status_code=status.HTTP_200_OK,
    summary="Прикрепить ученика к преподавателю",
)
def add_student(
    request: AddStudentRequest,
    current_user: CurrentUserDep,
    service: TeacherServiceDep,
) -> TeacherResponse:
    dto = service.add_student(
        teacher_id=current_user.id,
        student_id=request.student_id,
    )
    return TeacherResponse.from_dto(dto)


@router.delete(
    "/me/students/{student_id}",
    response_model=TeacherResponse,
    status_code=status.HTTP_200_OK,
    summary="Открепить ученика от преподавателя",
)
def remove_student(
    student_id: UUID,
    current_user: CurrentUserDep,
    service: TeacherServiceDep,
) -> TeacherResponse:
    dto = service.remove_student(
        teacher_id=current_user.id,
        student_id=student_id,
    )
    return TeacherResponse.from_dto(dto)


@router.post(
    "/me/students/favourites",
    response_model=BatchAddProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Добавить товар в избранное всем своим ученикам",
)
def add_product_to_all_students(
    request: AddProductToStudentsRequest,
    current_user: CurrentUserDep,
    service: TeacherServiceDep,
) -> BatchAddProductResponse:
    dto = service.add_product_to_all_students(
        teacher_id=current_user.id,
        dto=request.to_dto(),
    )
    return BatchAddProductResponse.from_dto(dto)
