from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from application.product.dto import ProductFilterDto
from application.product.exceptions import (
    InsufficientStockException,
    InvalidProductDataException,
    ProductNotFoundException,
)

from .dependencies import ProductServiceDep
from .schemas import (
    CreateProductRequest,
    ProductListResponse,
    ProductResponse,
    StockOperationRequest,
    UpdateProductRequest,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить каталог товаров с фильтрацией и пагинацией",
)
def list_products(
    service: ProductServiceDep,
    query: Annotated[
        str | None,
        Query(description="Поисковый запрос по названию или описанию"),
    ] = None,
    min_price: Annotated[
        Decimal | None,
        Query(ge=0, description="Минимальная цена"),
    ] = None,
    max_price: Annotated[
        Decimal | None,
        Query(ge=0, description="Максимальная цена"),
    ] = None,
    in_stock_only: Annotated[
        bool,
        Query(description="Только товары в наличии"),
    ] = False,
    offset: Annotated[
        int,
        Query(ge=0, description="Смещение (offset)"),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Лимит на страницу"),
    ] = 50,
) -> ProductListResponse:
    filter_dto = ProductFilterDto(
        query=query,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        offset=offset,
        limit=limit,
    )
    result = service.list(filter_dto)
    return ProductListResponse.from_dto(result)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый товар",
)
def create_product(
    request: CreateProductRequest,
    service: ProductServiceDep,
) -> ProductResponse:
    try:
        dto = request.to_dto()
        product_dto = service.create(dto)
        return ProductResponse.from_dto(product_dto)
    except InvalidProductDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить товар по ID",
)
def get_product_by_id(
    product_id: UUID,
    service: ProductServiceDep,
) -> ProductResponse:
    try:
        product_dto = service.get_by_id(product_id)
        return ProductResponse.from_dto(product_dto)
    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить данные товара",
)
def update_product(
    product_id: UUID,
    request: UpdateProductRequest,
    service: ProductServiceDep,
) -> ProductResponse:
    try:
        dto = request.to_dto()
        product_dto = service.update(product_id, dto)
        return ProductResponse.from_dto(product_dto)
    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidProductDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар",
)
def delete_product(
    product_id: UUID,
    service: ProductServiceDep,
) -> None:
    try:
        service.delete(product_id)
    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{product_id}/reserve",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Зарезервировать количество товара на складе",
)
def reserve_stock(
    product_id: UUID,
    request: StockOperationRequest,
    service: ProductServiceDep,
) -> ProductResponse:
    try:
        product_dto = service.reserve_stock(product_id, request.amount)
        return ProductResponse.from_dto(product_dto)
    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (InsufficientStockException, InvalidProductDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{product_id}/restore",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Вернуть зарезервированное количество товара на склад",
)
def restore_stock(
    product_id: UUID,
    request: StockOperationRequest,
    service: ProductServiceDep,
) -> ProductResponse:
    try:
        product_dto = service.restore_stock(product_id, request.amount)
        return ProductResponse.from_dto(product_dto)
    except ProductNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidProductDataException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
