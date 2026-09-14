import re
from collections.abc import Awaitable, Callable, Collection, MutableMapping
from dataclasses import dataclass
from typing import Any, Self

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from domain.user import UserRole

from .authentication_middleware import get_current_user

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


@dataclass(frozen=True)
class RouteAuthRule:
    """Правило авторизации для пути/эндпоинта."""

    path: str
    allowed_roles: frozenset[UserRole]
    methods: frozenset[str] | None = None
    exact_match: bool = False

    @classmethod
    def create(
        cls,
        path: str,
        allowed_roles: Collection[UserRole],
        methods: Collection[str] | None = None,
        exact_match: bool = False,
    ) -> Self:
        return cls(
            path=path,
            allowed_roles=frozenset(allowed_roles),
            methods=frozenset(m.upper() for m in methods) if methods else None,
            exact_match=exact_match,
        )

    def matches(self, request_path: str, request_method: str) -> bool:
        if self.methods is not None and request_method.upper() not in self.methods:
            return False

        if "{" in self.path and "}" in self.path:
            pattern = re.sub(r"\{[^}]+}", r"[^/]+", self.path)
            return bool(re.fullmatch(pattern, request_path))

        if self.exact_match:
            return request_path == self.path
        return request_path.startswith(self.path)


def authorization_middleware(
    rules: list[RouteAuthRule] | None = None,
) -> Callable[[ASGIApp], ASGIApp]:
    """Фабрика ASGI-мидлвари ролевой авторизации для заданных эндпоинтов."""
    active_rules = rules or []

    def middleware_factory(app: ASGIApp) -> ASGIApp:
        async def asgi_app(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            request = Request(scope, receive)
            path = request.url.path
            method = request.method

            for rule in active_rules:
                if rule.matches(path, method):
                    try:
                        user = get_current_user(request)
                    except HTTPException as exc:
                        response = JSONResponse(
                            status_code=exc.status_code,
                            content={"detail": exc.detail},
                        )
                        await response(scope, receive, send)
                        return

                    if user.role not in rule.allowed_roles:
                        response = JSONResponse(
                            status_code=403,
                            content={
                                "detail": "Недостаточно прав доступа для выполнения данной операции."
                            },
                        )
                        await response(scope, receive, send)
                        return
                    break

            await app(scope, receive, send)

        return asgi_app

    return middleware_factory
