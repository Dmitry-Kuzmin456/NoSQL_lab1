from uuid import UUID


class UserException(Exception):
    """Базовое исключение для операций с пользователями."""


class UserNotFoundException(UserException):
    def __init__(self, identifier: str | UUID):
        super().__init__(f"Пользователь '{identifier}' не найден.")
        self.identifier = identifier


class UserAlreadyExistsException(UserException):
    def __init__(self, email: str):
        super().__init__(f"Пользователь с email '{email}' уже зарегистрирован.")
        self.email = email


class InvalidCredentialsException(UserException):
    def __init__(self):
        super().__init__("Неверный email или пароль.")


class WeakPasswordException(UserException):
    def __init__(self, reason: str = "Пароль должен содержать не менее 6 символов."):
        super().__init__(reason)


class WeakNewPasswordException(UserException):
    def __init__(
        self,
        reason: str = "Новый пароль должен содержать как минимум 6 символов.",
    ):
        super().__init__(reason)
