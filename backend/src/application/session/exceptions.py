from uuid import UUID

from application.exceptions import ApplicationException


class SessionException(ApplicationException):
    """Базовое исключение для операций с сессиями."""

    status_code: int = 400


class SessionNotFoundException(SessionException):
    status_code: int = 404

    def __init__(self, identifier: str | UUID = "Unknown"):
        super().__init__(f"Сессия '{identifier}' не найдена.")
        self.identifier = identifier


class SessionExpiredException(SessionException):
    status_code: int = 401

    def __init__(self, message: str = "Срок действия сессии истёк."):
        super().__init__(message)


class SessionRevokedException(SessionException):
    status_code: int = 401

    def __init__(self, message: str = "Сессия была отозвана."):
        super().__init__(message)
