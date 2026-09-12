from typing import Annotated

from fastapi import Depends

from application.auth import AuthService
from application.session import ISessionRepository, SessionService
from infrastructure.http.user.dependencies import (
    PasswordHasherDep,
    UserServiceDep,
)


def get_session_repository() -> ISessionRepository:
    raise NotImplementedError("ISessionRepository adapter is not registered yet.")


SessionRepositoryDep = Annotated[ISessionRepository, Depends(get_session_repository)]


def get_session_service(
    session_repository: SessionRepositoryDep,
) -> SessionService:
    return SessionService(session_repository=session_repository)


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]


def get_auth_service(
    user_service: UserServiceDep,
    session_service: SessionServiceDep,
    password_hasher: PasswordHasherDep,
) -> AuthService:
    return AuthService(
        user_service=user_service,
        session_service=session_service,
        password_hasher=password_hasher,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
