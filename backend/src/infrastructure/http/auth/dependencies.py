from typing import Annotated

from fastapi import Depends

from application.auth import AuthService, ITokenService
from application.session import ISessionRepository, SessionService
from infrastructure.environment.settings import settings
from infrastructure.http.user.dependencies import (
    PasswordHasherDep,
    UserServiceDep,
)
from infrastructure.security import JwtTokenService

_token_service: ITokenService = JwtTokenService(
    secret_key=settings.auth.jwt_secret_key,
    algorithm=settings.auth.jwt_algorithm,
    expire_minutes=settings.auth.access_token_expire_minutes,
)


def get_token_service() -> ITokenService:
    return _token_service


TokenServiceDep = Annotated[ITokenService, Depends(get_token_service)]


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
    token_service: TokenServiceDep,
) -> AuthService:
    return AuthService(
        user_service=user_service,
        session_service=session_service,
        password_hasher=password_hasher,
        token_service=token_service,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
