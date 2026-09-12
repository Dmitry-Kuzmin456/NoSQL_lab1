from uuid import UUID


class SessionException(Exception):
    """Базовое исключение для операций с сессиями."""



class SessionNotFoundException(SessionException):
    def __init__(self, identifier: str | UUID = "Unknown"):
        super().__init__(f"Сессия '{identifier}' не найдена.")
        self.identifier = identifier


class SessionExpiredException(SessionException):
    def __init__(self, message: str = "Срок действия сессии истёк."):
        super().__init__(message)


class SessionRevokedException(SessionException):
    def __init__(self, message: str = "Сессия была отозвана."):
        super().__init__(message)
