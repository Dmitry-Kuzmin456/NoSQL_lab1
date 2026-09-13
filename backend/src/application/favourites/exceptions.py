from uuid import UUID

from application.exceptions import ApplicationException


class FavouritesException(ApplicationException):
    """Базовое исключение для операций с избранным."""

    status_code: int = 400


class FavouriteProductNotFoundException(FavouritesException):
    status_code: int = 404

    def __init__(self, product_id: UUID):
        super().__init__(f"Товар '{product_id}' не найден в избранном.")
        self.product_id = product_id


class FavouriteAlreadyExistsException(FavouritesException):
    status_code: int = 409

    def __init__(self, product_id: UUID):
        super().__init__(f"Товар '{product_id}' уже находится в избранном.")
        self.product_id = product_id
