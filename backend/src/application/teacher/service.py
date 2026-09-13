import logging
from uuid import UUID

from application.favourites.dto import AddFavouriteDto
from application.favourites.service import FavouritesService
from application.product.service import ProductService
from application.user.dto import UserResponseDto
from application.user.exceptions import UserNotFoundException
from application.user.service import UserService
from domain.teacher import Teacher
from domain.user import UserRole

from .dto import (
    AddProductToStudentsDto,
    BatchAddProductResultDto,
    TeacherResponseDto,
)
from .exceptions import (
    CannotAddSelfAsStudentException,
    InvalidStudentRoleException,
    StudentAlreadyAssignedException,
    StudentNotAssignedException,
    TeacherNotFoundException,
)
from .repository import ITeacherRepository

logger = logging.getLogger(__name__)


class TeacherService:
    def __init__(
        self,
        teacher_repository: ITeacherRepository,
        user_service: UserService,
        product_service: ProductService,
        favourites_service: FavouritesService,
    ):
        self._teacher_repository = teacher_repository
        self._user_service = user_service
        self._product_service = product_service
        self._favourites_service = favourites_service

    def get_teacher(self, teacher_id: UUID) -> TeacherResponseDto:
        teacher = self._get_teacher(teacher_id)
        return TeacherResponseDto.from_domain(teacher)

    def get_students(self, teacher_id: UUID) -> list[UserResponseDto]:
        teacher = self._get_teacher(teacher_id)
        students: list[UserResponseDto] = []
        for student_id in teacher.get_student_ids():
            try:
                student = self._user_service.get_by_id(student_id)
                students.append(student)
            except UserNotFoundException:
                logger.warning(
                    "Ученик '%s' прикреплен к преподавателю '%s', но не найден в системе",
                    student_id,
                    teacher_id,
                )
        return students

    def add_student(self, teacher_id: UUID, student_id: UUID) -> TeacherResponseDto:
        if teacher_id == student_id:
            raise CannotAddSelfAsStudentException()

        student = self._user_service.get_by_id(student_id)
        if student.role != UserRole.STUDENT:
            raise InvalidStudentRoleException(student_id)

        teacher = self._get_teacher(teacher_id)
        if teacher.has_student(student_id):
            raise StudentAlreadyAssignedException(student_id)

        teacher.add_student(student_id)
        saved = self._teacher_repository.save(teacher)
        return TeacherResponseDto.from_domain(saved)

    def remove_student(self, teacher_id: UUID, student_id: UUID) -> TeacherResponseDto:
        teacher = self._get_teacher(teacher_id)
        if not teacher.has_student(student_id):
            raise StudentNotAssignedException(student_id)

        teacher.remove_student(student_id)
        saved = self._teacher_repository.save(teacher)
        return TeacherResponseDto.from_domain(saved)

    def add_product_to_all_students(
        self,
        teacher_id: UUID,
        dto: AddProductToStudentsDto,
    ) -> BatchAddProductResultDto:
        self._product_service.get_by_id(dto.product_id)

        teacher = self._get_teacher(teacher_id)
        student_ids = teacher.get_student_ids()

        fav_dto = AddFavouriteDto(product_id=dto.product_id, note=dto.note)
        for student_id in student_ids:
            self._favourites_service.add_product(
                user_id=student_id,
                dto=fav_dto,
                added_by_user_id=teacher_id,
            )

        return BatchAddProductResultDto(
            product_id=dto.product_id,
            affected_students=len(student_ids),
            student_ids=student_ids,
        )

    def _get_teacher(self, teacher_id: UUID) -> Teacher:
        teacher = self._teacher_repository.get_by_id(teacher_id)
        if teacher is None:
            raise TeacherNotFoundException(teacher_id)
        return teacher
