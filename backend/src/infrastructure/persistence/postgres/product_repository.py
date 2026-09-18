from decimal import Decimal
from typing import Any
from uuid import UUID

from psycopg import sql
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from application.product.dto import ProductFilterDto
from application.product.repository import IProductRepository
from domain.product import Product
from infrastructure.persistence.postgres.connection import get_postgres_pool


class PostgresProductRepository(IProductRepository):
    """Репозиторий товаров для PostgreSQL."""

    def __init__(self, pool: ConnectionPool | None = None) -> None:
        self._pool: ConnectionPool = pool or get_postgres_pool()

    def get_by_id(self, product_id: UUID) -> Product | None:
        with (
            self._pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            cur.execute(
                "SELECT id, name, description, price, quantity FROM products WHERE id = %s",
                (product_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return Product(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                price=Decimal(str(row["price"])),
                quantity=row["quantity"],
            )

    def exists_by_id(self, product_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM products WHERE id = %s",
                (product_id,),
            )
            return cur.fetchone() is not None

    def list(
        self,
        filter_dto: ProductFilterDto | None = None,
    ) -> tuple[list[Product], int]:
        conditions: list[sql.SQL] = []
        params: list[Any] = []

        if filter_dto is not None:
            if filter_dto.query is not None and filter_dto.query.strip():
                pattern = f"%{filter_dto.query.strip()}%"
                conditions.append(sql.SQL("(name ILIKE %s OR description ILIKE %s)"))
                params.extend([pattern, pattern])
            if filter_dto.min_price is not None:
                conditions.append(sql.SQL("price >= %s"))
                params.append(filter_dto.min_price)
            if filter_dto.max_price is not None:
                conditions.append(sql.SQL("price <= %s"))
                params.append(filter_dto.max_price)
            if filter_dto.in_stock_only:
                conditions.append(sql.SQL("quantity > 0"))

        base_count: sql.SQL | sql.Composed = sql.SQL(
            "SELECT count(*) as count FROM products"
        )
        base_select: sql.SQL | sql.Composed = sql.SQL(
            "SELECT id, name, description, price, quantity FROM products"
        )

        if conditions:
            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)
            base_count = base_count + where_clause
            base_select = base_select + where_clause

        count_query = base_count
        select_query = base_select + sql.SQL(" ORDER BY name ASC LIMIT %s OFFSET %s")

        with (
            self._pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            cur.execute(count_query, params)
            total = int((cur.fetchone() or {}).get("count", 0))

            offset = filter_dto.offset if filter_dto else 0
            limit = filter_dto.limit if filter_dto else 50

            cur.execute(select_query, [*params, limit, offset])
            rows = cur.fetchall()

            products = [
                Product(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    price=Decimal(str(row["price"])),
                    quantity=row["quantity"],
                )
                for row in rows
            ]
            return products, total

    def save(self, product: Product) -> Product:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products (id, name, description, price, quantity)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price,
                    quantity = EXCLUDED.quantity
                """,
                (
                    product.id,
                    product.name,
                    product.description,
                    product.price,
                    product.quantity,
                ),
            )
            conn.commit()
            return product

    def update_stock(self, product_id: UUID, delta: int) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                    UPDATE products
                    SET quantity = quantity + %s
                    WHERE id = %s AND (quantity + %s) >= 0
                    """,
                (delta, product_id, delta),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete(self, product_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,),
            )
            conn.commit()
            return cur.rowcount > 0
