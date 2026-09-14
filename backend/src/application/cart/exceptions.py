from uuid import UUID

from application.exceptions import ApplicationException


class CartException(ApplicationException):
    """Базовое исключение для операций с корзиной."""

    status_code: int = 400


class CartProductNotFoundException(CartException):
    status_code: int = 404

    def __init__(self, product_id: UUID) -> None:
        super().__init__(f"Товар '{product_id}' не найден в корзине.")
        self.product_id = product_id


class InvalidCartQuantityException(CartException):
    status_code: int = 400

    def __init__(
        self, message: str = "Количество товара должно быть больше 0."
    ) -> None:
        super().__init__(message)


class CartIsEmptyException(CartException):
    status_code: int = 400

    def __init__(self, message: str = "Корзина пуста.") -> None:
        super().__init__(message)
