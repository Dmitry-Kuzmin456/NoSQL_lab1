from collections.abc import Awaitable, Callable, MutableMapping
from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status

from application.auth.token import ITokenService
from domain.user import UserRole

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


@dataclass(frozen=True)
class AuthUser:
    id: UUID
    role: UserRole


def authentication_middleware(
    token_service: ITokenService,
) -> Callable[[ASGIApp], ASGIApp]:
    """Фабрика ASGI-мидлвари аутентификации пользователя по токену из заголовка Authorization."""

    def middleware_factory(app: ASGIApp) -> ASGIApp:
        async def asgi_app(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            request = Request(scope, receive)
            auth_header = request.headers.get("Authorization")
            token: str | None = None

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()

            request.state.user = None
            if token:
                try:
                    payload = token_service.verify_access_token(token)
                    user_id = UUID(str(payload["user_id"]))
                    role = UserRole(payload["role"])
                    request.state.user = AuthUser(id=user_id, role=role)
                except (jwt.PyJWTError, KeyError, ValueError):
                    request.state.user = None

            await app(scope, receive, send)

        return asgi_app

    return middleware_factory


def get_current_user_optional(request: Request) -> AuthUser | None:
    return getattr(request.state, "user", None)


OptionalCurrentUserDep = Annotated[AuthUser | None, Depends(get_current_user_optional)]


def get_current_user(request: Request) -> AuthUser:
    user = get_current_user_optional(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не аутентифицирован.",
        )
    return user


CurrentUserDep = Annotated[AuthUser, Depends(get_current_user)]
