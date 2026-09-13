from uuid import UUID

from application.exceptions import ApplicationException


class UserException(ApplicationException):
    """Базовое исключение для операций с пользователями."""

    status_code: int = 400


class UserNotFoundException(UserException):
    status_code: int = 404

    def __init__(self, identifier: str | UUID):
        super().__init__(f"Пользователь '{identifier}' не найден.")
        self.identifier = identifier


class UserAlreadyExistsException(UserException):
    status_code: int = 409

    def __init__(self, email: str):
        super().__init__(f"Пользователь с email '{email}' уже зарегистрирован.")
        self.email = email


class InvalidCredentialsException(UserException):
    status_code: int = 401

    def __init__(self):
        super().__init__("Неверный email или пароль.")


class WeakPasswordException(UserException):
    status_code: int = 400

    def __init__(self, reason: str = "Пароль должен содержать не менее 6 символов."):
        super().__init__(reason)


class WeakNewPasswordException(UserException):
    status_code: int = 400

    def __init__(
        self,
        reason: str = "Новый пароль должен содержать как минимум 6 символов.",
    ):
        super().__init__(reason)
