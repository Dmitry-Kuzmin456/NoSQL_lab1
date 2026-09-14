from decimal import Decimal
from uuid import UUID

from domain.product import Product

from .dto import (
    ProductCreateDto,
    ProductFilterDto,
    ProductListResponseDto,
    ProductResponseDto,
    ProductUpdateDto,
)
from .exceptions import (
    EmptyProductNameException,
    InsufficientStockException,
    InvalidStockAmountException,
    NegativeProductPriceException,
    NegativeProductQuantityException,
    ProductNotFoundException,
)
from .repository import IProductRepository


class ProductService:
    def __init__(self, product_repository: IProductRepository) -> None:
        self._product_repository = product_repository

    def create(self, dto: ProductCreateDto) -> ProductResponseDto:
        if not dto.name.strip():
            raise EmptyProductNameException()
        if dto.price < Decimal("0.00"):
            raise NegativeProductPriceException()
        if dto.quantity < 0:
            raise NegativeProductQuantityException()

        product = Product(
            name=dto.name.strip(),
            description=dto.description.strip(),
            price=dto.price,
            quantity=dto.quantity,
        )
        saved_product = self._product_repository.save(product)
        return ProductResponseDto.from_domain(saved_product)

    def get_by_id(self, product_id: UUID) -> ProductResponseDto:
        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundException(product_id)
        return ProductResponseDto.from_domain(product)

    def list(
        self,
        filter_dto: ProductFilterDto | None = None,
    ) -> ProductListResponseDto:
        if filter_dto is None:
            filter_dto = ProductFilterDto()

        items, total = self._product_repository.list(filter_dto=filter_dto)
        return ProductListResponseDto(
            items=[ProductResponseDto.from_domain(p) for p in items],
            total=total,
            offset=filter_dto.offset,
            limit=filter_dto.limit,
        )

    def update(self, product_id: UUID, dto: ProductUpdateDto) -> ProductResponseDto:
        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundException(product_id)

        if dto.name is not None:
            if not dto.name.strip():
                raise EmptyProductNameException()
            product.name = dto.name.strip()

        if dto.description is not None:
            product.description = dto.description.strip()

        if dto.price is not None:
            if dto.price < Decimal("0.00"):
                raise NegativeProductPriceException()
            product.price = dto.price

        if dto.quantity is not None:
            if dto.quantity < 0:
                raise NegativeProductQuantityException()
            product.quantity = dto.quantity

        saved_product = self._product_repository.save(product)
        return ProductResponseDto.from_domain(saved_product)

    def delete(self, product_id: UUID) -> bool:
        if not self._product_repository.exists_by_id(product_id):
            raise ProductNotFoundException(product_id)
        return self._product_repository.delete(product_id)

    def reserve_stock(self, product_id: UUID, amount: int) -> ProductResponseDto:
        if amount <= 0:
            raise InvalidStockAmountException()

        if not self._product_repository.exists_by_id(product_id):
            raise ProductNotFoundException(product_id)

        if not self._product_repository.update_stock(product_id, -amount):
            product = self._product_repository.get_by_id(product_id)
            available = product.quantity if product else 0
            raise InsufficientStockException(
                product_id=product_id,
                requested=amount,
                available=available,
            )

        saved = self._product_repository.get_by_id(product_id)
        assert saved is not None
        return ProductResponseDto.from_domain(saved)

    def restore_stock(self, product_id: UUID, amount: int) -> ProductResponseDto:
        if amount <= 0:
            raise InvalidStockAmountException()

        if not self._product_repository.update_stock(product_id, amount):
            raise ProductNotFoundException(product_id)

        saved = self._product_repository.get_by_id(product_id)
        assert saved is not None
        return ProductResponseDto.from_domain(saved)
