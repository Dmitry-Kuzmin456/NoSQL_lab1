class ApplicationException(Exception):
    """Базовое исключение уровня приложения."""

    status_code: int = 400

    def __init__(self, message: str = "Ошибка приложения.") -> None:
        super().__init__(message)
        self.message = message
