from uuid import UUID

from application.exceptions import ApplicationException


class OrderException(ApplicationException):
    """Базовое исключение для операций с заказами."""

    status_code: int = 400


class OrderNotFoundException(OrderException):
    status_code: int = 404

    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Заказ '{order_id}' не найден.")
        self.order_id = order_id


class InvalidOrderStatusException(OrderException):
    status_code: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidOrderQuantityException(OrderException):
    status_code: int = 400

    def __init__(
        self, message: str = "Количество товара в заказе должно быть больше 0."
    ) -> None:
        super().__init__(message)
