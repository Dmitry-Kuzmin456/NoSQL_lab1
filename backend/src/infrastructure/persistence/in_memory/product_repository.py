import copy
import threading
from uuid import UUID

from application.product.dto import ProductFilterDto
from application.product.repository import IProductRepository
from domain.product import Product


class InMemoryProductRepository(IProductRepository):
    def __init__(self) -> None:
        self._products: dict[UUID, Product] = {}
        self._lock = threading.RLock()

    def get_by_id(self, product_id: UUID) -> Product | None:
        with self._lock:
            product = self._products.get(product_id)
            if product is None:
                return None
            return copy.deepcopy(product)

    def exists_by_id(self, product_id: UUID) -> bool:
        with self._lock:
            return product_id in self._products

    def list(
        self,
        filter_dto: ProductFilterDto | None = None,
    ) -> tuple[list[Product], int]:
        with self._lock:
            items = list(self._products.values())

            if filter_dto is not None:
                paginated, total = filter_dto.apply(items)
            else:
                total = len(items)
                paginated = items[:50]

            return [copy.deepcopy(p) for p in paginated], total

    def save(self, product: Product) -> Product:
        with self._lock:
            self._products[product.id] = copy.deepcopy(product)
            return copy.deepcopy(product)

    def update_stock(self, product_id: UUID, delta: int) -> bool:
        with self._lock:
            product = self._products.get(product_id)
            if product is None:
                return False
            if product.quantity + delta < 0:
                return False
            product.quantity += delta
            return True

    def delete(self, product_id: UUID) -> bool:
        with self._lock:
            if product_id in self._products:
                del self._products[product_id]
                return True
            return False
