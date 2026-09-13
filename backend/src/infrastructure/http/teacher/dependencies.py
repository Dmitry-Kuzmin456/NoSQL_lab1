from typing import Annotated

from fastapi import Depends

from application.teacher.repository import ITeacherRepository
from application.teacher.service import TeacherService
from infrastructure.http.favourites.dependencies import FavouritesServiceDep
from infrastructure.http.product.dependencies import ProductServiceDep
from infrastructure.http.user.dependencies import (
    UserServiceDep,
    get_user_repository,
)
from infrastructure.persistence.in_memory.teacher_repository import (
    InMemoryTeacherRepository,
)

_teacher_repository: ITeacherRepository = InMemoryTeacherRepository(
    user_repository=get_user_repository()
)


def get_teacher_repository() -> ITeacherRepository:
    return _teacher_repository


TeacherRepositoryDep = Annotated[ITeacherRepository, Depends(get_teacher_repository)]


def get_teacher_service(
    teacher_repository: TeacherRepositoryDep,
    user_service: UserServiceDep,
    product_service: ProductServiceDep,
    favourites_service: FavouritesServiceDep,
) -> TeacherService:
    return TeacherService(
        teacher_repository=teacher_repository,
        user_service=user_service,
        product_service=product_service,
        favourites_service=favourites_service,
    )


TeacherServiceDep = Annotated[TeacherService, Depends(get_teacher_service)]
