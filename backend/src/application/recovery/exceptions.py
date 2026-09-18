from application.exceptions import ApplicationException


class RecoveryTokenException(ApplicationException):
    """Базовое исключение для токенов восстановления."""

    status_code: int = 400


class RecoveryTokenNotFoundException(RecoveryTokenException):
    status_code: int = 404

    def __init__(self, token: str | None = None) -> None:
        message = (
            f"Токен восстановления '{token}' не найден."
            if token
            else "Токен восстановления не найден."
        )
        super().__init__(message)
        self.token = token


class RecoveryTokenExpiredException(RecoveryTokenException):
    status_code: int = 400

    def __init__(self) -> None:
        super().__init__("Срок действия токена восстановления истек.")
