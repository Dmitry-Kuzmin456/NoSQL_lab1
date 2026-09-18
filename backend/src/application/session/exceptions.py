from application.exceptions import ApplicationException


class SessionException(ApplicationException):
    """Базовое исключение для операций с сессиями."""

    status_code: int = 400


class SessionNotFoundException(SessionException):
    status_code: int = 404

    def __init__(self, token: str = "Unknown"):
        super().__init__(f"Сессия '{token}' не найдена.")
        self.token = token


class SessionExpiredException(SessionException):
    status_code: int = 401

    def __init__(self, message: str = "Срок действия сессии истёк."):
        super().__init__(message)
