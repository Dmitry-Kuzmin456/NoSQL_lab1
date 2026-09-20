from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from psycopg import sql
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from application.product.dto import (
    ProductFilterDto,
    ProductSortBy,
)
from application.product.repository import IProductRepository
from domain.product import Product
from infrastructure.persistence.postgres.connection import get_postgres_pool


class PostgresProductRepository(IProductRepository):
    """Репозиторий товаров для PostgreSQL."""

    def __init__(self, pool: ConnectionPool | None = None) -> None:
        self._pool: ConnectionPool = pool or get_postgres_pool()

    @staticmethod
    def _row_to_product(row: Any) -> Product:
        return Product(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            price=Decimal(str(row["price"])),
            quantity=row["quantity"],
        )

    def get_by_id(self, product_id: UUID) -> Product | None:
        with self._pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, name, description, price, quantity FROM products WHERE id = %s",
                (product_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_product(row)

    def get_by_ids(self, product_ids: list[UUID]) -> list[Product]:
        if not product_ids:
            return []
        with self._pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, name, description, price, quantity FROM products WHERE id = ANY(%s)",
                (product_ids,),
            )
            rows = cur.fetchall()
            return [self._row_to_product(r) for r in rows]

    def exists_by_id(self, product_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM products WHERE id = %s", (product_id,))
            return cur.fetchone() is not None

    def list(
        self,
        filter_dto: ProductFilterDto | None = None,
    ) -> list[Product]:
        conditions: list[sql.SQL] = []
        params: list[Any] = []

        if filter_dto is not None:
            if filter_dto.query is not None and filter_dto.query.strip():
                pattern = f"%{filter_dto.query.strip()}%"
                conditions.append(
                    sql.SQL("(p.name ILIKE %s OR p.description ILIKE %s)")
                )
                params.extend([pattern, pattern])
            if filter_dto.min_price is not None:
                conditions.append(sql.SQL("p.price >= %s"))
                params.append(filter_dto.min_price)
            if filter_dto.max_price is not None:
                conditions.append(sql.SQL("p.price <= %s"))
                params.append(filter_dto.max_price)
            if filter_dto.in_stock_only:
                conditions.append(sql.SQL("p.quantity > 0"))

        where_clause: sql.SQL | sql.Composed = sql.SQL("")
        if conditions:
            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)

        if filter_dto and filter_dto.sort_by == ProductSortBy.PRICE_ASC:
            order_by = sql.SQL("ORDER BY price")
        elif filter_dto and filter_dto.sort_by == ProductSortBy.PRICE_DESC:
            order_by = sql.SQL("ORDER BY price DESC")
        elif filter_dto and filter_dto.sort_by == ProductSortBy.POPULARITY:
            order_by = sql.SQL("ORDER BY total_sold DESC")
        elif filter_dto and filter_dto.sort_by == ProductSortBy.NAME_DESC:
            order_by = sql.SQL("ORDER BY name DESC")
        elif filter_dto and filter_dto.sort_by == ProductSortBy.NEWEST:
            order_by = sql.SQL("ORDER BY id DESC")
        else:
            order_by = sql.SQL("ORDER BY name")

        offset = filter_dto.offset if filter_dto else 0
        limit = filter_dto.limit if filter_dto else 50

        query = sql.SQL(
            """
            WITH product_sales AS (
                SELECT DISTINCT
                    product_id,
                    SUM(quantity) OVER (PARTITION BY product_id) AS total_sold
                FROM orders
            ),
            filtered_products AS (
                SELECT
                    p.id,
                    p.name,
                    p.description,
                    p.price,
                    p.quantity,
                    COALESCE(s.total_sold, 0) AS total_sold
                FROM products p
                LEFT JOIN product_sales s ON p.id = s.product_id
                {where_clause}
            )
            SELECT id, name, description, price, quantity, total_sold
            FROM filtered_products
            {order_by}
            LIMIT %s OFFSET %s
            """
        ).format(where_clause=where_clause, order_by=order_by)

        with self._pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, [*params, limit, offset])
            rows = cur.fetchall()
            return [self._row_to_product(r) for r in rows]

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

    def update_stock_and_get(self, product_id: UUID, delta: int) -> Product | None:
        with self._pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE products
                SET quantity = quantity + %s
                WHERE id = %s AND (quantity + %s) >= 0
                RETURNING id, name, description, price, quantity
                """,
                (delta, product_id, delta),
            )
            row = cur.fetchone()
            conn.commit()
            if row is None:
                return None
            return self._row_to_product(row)

    def delete(self, product_id: UUID) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            return cur.rowcount > 0
