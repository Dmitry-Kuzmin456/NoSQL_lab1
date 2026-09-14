from application.exceptions import ApplicationException


class CheckoutException(ApplicationException):
    """Базовое исключение для операций оформления заказа."""

    status_code: int = 400


class EmptyCartCheckoutException(CheckoutException):
    status_code: int = 400

    def __init__(
        self, message: str = "Невозможно оформить заказ: корзина пуста."
    ) -> None:
        super().__init__(message)
