from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from domain.user import UserRole
from infrastructure.http.auth.dependencies import RoleChecker
from infrastructure.http.middleware.authentication_middleware import get_current_user


def _collect_api_routes(
    routes: list[Any], prefix: str = ""
) -> list[tuple[str, APIRoute]]:
    """Рекурсивно собирает все APIRoute с учетом вложенных роутеров и префиксов."""
    collected: list[tuple[str, APIRoute]] = []
    for r in routes:
        if isinstance(r, APIRoute):
            collected.append((prefix + r.path, r))
        elif hasattr(r, "original_router"):
            inc_prefix = getattr(getattr(r, "include_context", None), "prefix", "")
            collected.extend(
                _collect_api_routes(r.original_router.routes, prefix + inc_prefix)
            )
        elif hasattr(r, "routes"):
            collected.extend(_collect_api_routes(r.routes, prefix))
    return collected


def _extract_auth_info(dependant: Any) -> tuple[bool, set[UserRole]]:
    """Рекурсивно извлекает информацию об авторизации и требуемых ролях из зависимостей маршрута."""
    is_authenticated = False
    required_roles: set[UserRole] = set()

    for dep in getattr(dependant, "dependencies", []):
        call = getattr(dep, "call", None)
        if isinstance(call, RoleChecker):
            is_authenticated = True
            if call.allowed_roles:
                required_roles.update(call.allowed_roles)
        elif call is get_current_user:
            is_authenticated = True

        sub_auth, sub_roles = _extract_auth_info(dep)
        if sub_auth:
            is_authenticated = True
        required_roles.update(sub_roles)

    return is_authenticated, required_roles


def custom_openapi_factory(app: FastAPI) -> Callable[[], dict[str, Any]]:
    """Фабрика функции кастомной OpenAPI схемы с автоматическим добавлением метаданных о ролях."""

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema

        openapi_schema: dict[str, Any] = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            summary=app.summary,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
        )

        components = openapi_schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Access Token (в заголовке `Authorization: Bearer <token>` или cookie `access_token`)",
        }

        components_schemas = components.setdefault("schemas", {})
        if "ErrorDetailResponse" not in components_schemas:
            components_schemas["ErrorDetailResponse"] = {
                "title": "ErrorDetailResponse",
                "type": "object",
                "properties": {
                    "detail": {
                        "title": "Detail",
                        "type": "string",
                        "description": "Описание ошибки",
                    }
                },
                "required": ["detail"],
            }

        paths: dict[str, Any] = openapi_schema.get("paths", {})
        collected_routes = _collect_api_routes(app.routes)

        for path, route in collected_routes:
            if path not in paths:
                continue

            methods = route.methods
            if not isinstance(methods, (set, list, tuple)):
                continue

            is_auth, roles = _extract_auth_info(route.dependant)
            if not is_auth:
                continue

            for method in methods:
                method_lower = str(method).lower()
                op = paths[path].get(method_lower)
                if not op:
                    continue

                op.setdefault("security", [{"BearerAuth": []}])

                if roles:
                    sorted_roles = sorted([r.value for r in roles])
                    op["x-required-roles"] = sorted_roles
                    roles_str = ", ".join(f"`{r}`" for r in sorted_roles)
                    badge = f"**Требуемые роли:** {roles_str}"
                else:
                    op["x-required-roles"] = ["AUTHENTICATED"]
                    badge = "**Требуемые роли:** Любой авторизованный пользователь"

                existing_desc = op.get("description", "")
                if badge not in existing_desc:
                    if existing_desc:
                        op["description"] = f"{badge}\n\n{existing_desc}"
                    else:
                        op["description"] = badge

                responses = op.setdefault("responses", {})
                if "401" not in responses:
                    responses["401"] = {
                        "description": "Пользователь не аутентифицирован.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorDetailResponse"
                                }
                            }
                        },
                    }

                if roles and "403" not in responses:
                    responses["403"] = {
                        "description": "Недостаточно прав доступа для выполнения данной операции.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorDetailResponse"
                                }
                            }
                        },
                    }

        app.openapi_schema = openapi_schema
        return openapi_schema

    return custom_openapi
