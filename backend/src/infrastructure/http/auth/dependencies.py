from typing import Annotated

from fastapi import Depends, HTTPException, status

from application.auth.service import AuthService
from application.auth.token import ITokenService
from application.session.repository import ISessionRepository
from application.session.service import SessionService
from domain.user import UserRole
from infrastructure.environment.settings import settings
from infrastructure.http.middleware.authentication_middleware import (
    AuthUser,
    get_current_user,
)
from infrastructure.http.user.dependencies import (
    PasswordHasherDep,
    UserServiceDep,
)
from infrastructure.persistence.in_memory.session_repository import (
    InMemorySessionRepository,
)
from infrastructure.security.jwt_service import JwtTokenService

_token_service: ITokenService = JwtTokenService(
    secret_key=settings.auth.jwt_secret_key,
    algorithm=settings.auth.jwt_algorithm,
    expire_minutes=settings.auth.access_token_expire_minutes,
)
_session_repository: ISessionRepository = InMemorySessionRepository()


def get_token_service() -> ITokenService:
    return _token_service


TokenServiceDep = Annotated[ITokenService, Depends(get_token_service)]


def get_session_repository() -> ISessionRepository:
    return _session_repository


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
 
 
def require_roles(*allowed_roles: UserRole):
    """Фабрика зависимости для проверки ролевого доступа пользователя."""

    def role_checker(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if allowed_roles and user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав доступа для выполнения данной операции.",
            )
        return user

    return Depends(role_checker)

