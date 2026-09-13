from typing import Annotated

from fastapi import Depends

from application.user import IPasswordHasher, IUserRepository, UserService
from infrastructure.persistence import InMemoryUserRepository
from infrastructure.security import BcryptPasswordHasher

_password_hasher: IPasswordHasher = BcryptPasswordHasher(rounds=12)
_user_repository: IUserRepository = InMemoryUserRepository()


def get_user_repository() -> IUserRepository:
    return _user_repository


def get_password_hasher() -> IPasswordHasher:
    return _password_hasher


UserRepositoryDep = Annotated[IUserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[IPasswordHasher, Depends(get_password_hasher)]


def get_user_service(
    user_repository: UserRepositoryDep,
    password_hasher: PasswordHasherDep,
) -> UserService:
    return UserService(
        user_repository=user_repository,
        password_hasher=password_hasher,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
