from typing import Annotated

from fastapi import Depends

from application.favourites.repository import IFavouritesRepository
from application.favourites.service import FavouritesService
from infrastructure.http.product.dependencies import ProductServiceDep
from infrastructure.persistence.in_memory.favourites_repository import (
    InMemoryFavouritesRepository,
)

_favourites_repository: IFavouritesRepository = InMemoryFavouritesRepository()


def get_favourites_repository() -> IFavouritesRepository:
    return _favourites_repository


FavouritesRepositoryDep = Annotated[
    IFavouritesRepository, Depends(get_favourites_repository)
]


def get_favourites_service(
    favourites_repository: FavouritesRepositoryDep,
    product_service: ProductServiceDep,
) -> FavouritesService:
    return FavouritesService(
        favourites_repository=favourites_repository,
        product_service=product_service,
    )


FavouritesServiceDep = Annotated[FavouritesService, Depends(get_favourites_service)]
