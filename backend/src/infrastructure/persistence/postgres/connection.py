import logging
from pathlib import Path

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from infrastructure.environment.settings import settings

logger = logging.getLogger(__name__)

_INIT_SQL = Path(__file__).resolve().parents[4] / "scripts" / "init_postgres.sql"
_pool: ConnectionPool | None = None


def get_postgres_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=settings.postgres.conninfo,
            min_size=settings.postgres.min_connections,
            max_size=settings.postgres.max_connections,
            open=True,
            kwargs={"row_factory": dict_row},
        )
    assert _pool is not None
    return _pool


def close_postgres_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def init_db(pool: ConnectionPool | None = None) -> None:
    if not _INIT_SQL.exists():
        logger.warning("PostgreSQL init script not found at %s", _INIT_SQL)
        return

    p = pool or get_postgres_pool()
    with p.connection() as conn, conn.cursor() as cur:
        cur.execute(_INIT_SQL.read_bytes())
        conn.commit()
    logger.info("PostgreSQL schema initialized from %s", _INIT_SQL.name)
