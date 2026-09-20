from uuid import UUID

from application.event_bus import IEventBus
from application.product.service import ProductService
from domain.favourites import FavouriteProduct, Favourites
from domain.history import OperationEvent, OperationType

from .dto import AddFavouriteDto, FavouriteItemResponseDto, FavouritesResponseDto
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

    def _build_response_dto(self, favourites: Favourites) -> FavouritesResponseDto:
        if not favourites.products:
            return FavouritesResponseDto(
                user_id=favourites.user_id,
                products=[],
                total_count=0,
            )

        product_ids = [p.product_id for p in favourites.products]
        products_map = self._product_service.get_by_ids(product_ids)

        items: list[FavouriteItemResponseDto] = []
        for item in favourites.products:
            prod_dto = products_map.get(item.product_id)
            if prod_dto is not None:
                items.append(
                    FavouriteItemResponseDto(
                        product_id=item.product_id,
                        added_user_id=item.added_user_id,
                        updated_at=item.updated_at,
                        product=prod_dto,
                        is_available=True,
                    )
                )
            else:
                items.append(
                    FavouriteItemResponseDto(
                        product_id=item.product_id,
                        added_user_id=item.added_user_id,
                        updated_at=item.updated_at,
                        product=None,
                        is_available=False,
                    )
                )

        return FavouritesResponseDto(
            user_id=favourites.user_id,
            products=items,
            total_count=len(items),
        )

    def get_by_user_id(self, user_id: UUID) -> FavouritesResponseDto:
        favourites = self._get_or_create(user_id)
        return self._build_response_dto(favourites)

    def is_in_favourites(self, user_id: UUID, product_id: UUID) -> bool:
        favourites = self._favourites_repository.get_by_user_id(user_id)
        if favourites is None:
            return False
        return favourites.has_product(product_id)

    def add_product(
        self,
        user_id: UUID,
        dto: AddFavouriteDto,
        added_by_user_id: UUID | None = None,
        check_product_exists: bool = True,
    ) -> FavouritesResponseDto:
        if check_product_exists:
            self._product_service.ensure_exists(dto.product_id)

        acting_user_id = added_by_user_id or user_id
        item = FavouriteProduct(
            product_id=dto.product_id,
            added_user_id=acting_user_id,
        )
        favourites = self._favourites_repository.add_item_and_get(
            user_id=user_id, item=item
        )

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.ADD_FAVOURITE,
                target_id=dto.product_id,
            )
        )

        return self._build_response_dto(favourites)

    def remove_product(
        self,
        user_id: UUID,
        product_id: UUID,
    ) -> FavouritesResponseDto:
        favourites = self._get_or_create(user_id)
        if not favourites.has_product(product_id):
            raise FavouriteProductNotFoundException(product_id)

        updated_favs = self._favourites_repository.remove_item_and_get(
            user_id, product_id
        )

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.REMOVE_FAVOURITE,
                target_id=product_id,
            )
        )

        return self._build_response_dto(updated_favs)

    def clear(self, user_id: UUID) -> FavouritesResponseDto:
        self._favourites_repository.delete_by_user_id(user_id)

        self._event_bus.publish(
            OperationEvent(
                user_id=user_id,
                action=OperationType.CLEAR_FAVOURITES,
            )
        )
        return self._build_response_dto(Favourites(user_id=user_id))

    def _get_or_create(self, user_id: UUID) -> Favourites:
        favourites = self._favourites_repository.get_by_user_id(user_id)
        if favourites is None:
            favourites = Favourites(user_id=user_id)
        return favourites
