from fastapi import Response

from infrastructure.environment.settings import settings


class CookieManager:
    """Менеджер для установки и очистки авторизационных cookie."""

    @staticmethod
    def set_auth_cookies(
        response: Response,
        access_token: str,
        refresh_token: str,
    ) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=settings.auth.cookie_httponly,
            samesite=settings.auth.cookie_samesite,
            secure=settings.auth.cookie_secure,
            max_age=settings.auth.access_token_expire_minutes * 60,
            path="/",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=settings.auth.cookie_httponly,
            samesite=settings.auth.cookie_samesite,
            secure=settings.auth.cookie_secure,
            max_age=settings.auth.refresh_token_expire_days * 86400,
            path="/",
        )

    @staticmethod
    def clear_auth_cookies(response: Response) -> None:
        for key in ("access_token", "refresh_token"):
            for secure in (True, False):
                response.delete_cookie(
                    key=key,
                    path="/",
                    secure=secure,
                    httponly=settings.auth.cookie_httponly,
                    samesite=settings.auth.cookie_samesite,
                )
