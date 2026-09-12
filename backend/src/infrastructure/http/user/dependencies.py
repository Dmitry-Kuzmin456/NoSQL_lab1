from typing import Annotated

from fastapi import Depends

from application.user import IPasswordHasher, IUserRepository, UserService
from infrastructure.security import BcryptPasswordHasher

_password_hasher: IPasswordHasher = BcryptPasswordHasher(rounds=12)


def get_user_repository() -> IUserRepository:
    raise NotImplementedError("IUserRepository adapter is not registered yet.")


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
