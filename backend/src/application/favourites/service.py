from uuid import UUID

from application.event_bus import IEventBus
from application.product.service import ProductService
from domain.favourites import Favourites
from domain.history import OperationEvent, OperationType

from .dto import AddFavouriteDto, FavouritesResponseDto
from .exceptions import FavouriteProductNotFoundException
from .repository import IFavouritesRepository


class FavouritesService:
    def __init__(
        self,
        favourites_repository: IFavouritesRepository,
        product_service: ProductService,
        event_bus: IEventBus,
    ):
        self._favourites_repository = favourites_repository
        self._product_service = product_service
        self._event_bus = event_bus

    def get_by_user_id(self, user_id: UUID) -> FavouritesResponseDto:
        favourites = self._get_or_create(user_id)
        return FavouritesResponseDto.from_domain(favourites)

    def add_product(
        self,
        user_id: UUID,
        dto: AddFavouriteDto,
        added_by_user_id: UUID | None = None,
    ) -> FavouritesResponseDto:
        self._product_service.get_by_id(dto.product_id)

        favourites = self._get_or_create(user_id)
        acting_user_id = added_by_user_id or user_id
        favourites.add_product(
            product_id=dto.product_id,
            added_user_id=acting_user_id,
            note=dto.note,
        )

        saved = self._favourites_repository.save(favourites)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.ADD_FAVOURITE,
                target_id=dto.product_id,
                details={"note": dto.note or ""},
            )
        )

        return FavouritesResponseDto.from_domain(saved)

    def remove_product(
        self,
        user_id: UUID,
        product_id: UUID,
    ) -> FavouritesResponseDto:
        favourites = self._get_or_create(user_id)
        if not favourites.has_product(product_id):
            raise FavouriteProductNotFoundException(product_id)

        favourites.remove_product(product_id)
        saved = self._favourites_repository.save(favourites)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.REMOVE_FAVOURITE,
                target_id=product_id,
            )
        )

        return FavouritesResponseDto.from_domain(saved)

    def is_in_favourites(self, user_id: UUID, product_id: UUID) -> bool:
        favourites = self._favourites_repository.get_by_user_id(user_id)
        if favourites is None:
            return False
        return favourites.has_product(product_id)

    def clear(self, user_id: UUID) -> FavouritesResponseDto:
        favourites = self._get_or_create(user_id)
        favourites.clear()
        saved = self._favourites_repository.save(favourites)
        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.CLEAR_FAVOURITES,
            )
        )
        return FavouritesResponseDto.from_domain(saved)

    def _get_or_create(self, user_id: UUID) -> Favourites:
        favourites = self._favourites_repository.get_by_user_id(user_id)
        if favourites is None:
            favourites = Favourites(user_id=user_id)
        return favourites
