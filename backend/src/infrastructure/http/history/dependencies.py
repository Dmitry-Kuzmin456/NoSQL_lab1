from typing import Annotated

from fastapi import Depends

from application.history.repository import (
    IHistoryRepository,
    IPostgresHistoryRepository,
    IRiakHistoryCacheRepository,
)
from application.history.service import HistoryService
from infrastructure.event_bus.dependencies import EventBusDep
from infrastructure.persistence.composite.history_repository import (
    CompositeHistoryRepository,
)
from infrastructure.persistence.postgres.history_repository import (
    PostgresHistoryRepository,
)
from infrastructure.persistence.riak.history_cache_repository import (
    RiakHistoryCacheRepository,
)

_postgres_history_repository: IPostgresHistoryRepository = (
    PostgresHistoryRepository()
)
_riak_history_cache_repository: IRiakHistoryCacheRepository = (
    RiakHistoryCacheRepository()
)
_history_repository: IHistoryRepository = CompositeHistoryRepository(
    postgres_repo=_postgres_history_repository,
    riak_repo=_riak_history_cache_repository,
)


def get_postgres_history_repository() -> IPostgresHistoryRepository:
    return _postgres_history_repository


def get_riak_history_cache_repository() -> IRiakHistoryCacheRepository:
    return _riak_history_cache_repository


def get_history_repository() -> IHistoryRepository:
    return _history_repository


HistoryRepositoryDep = Annotated[IHistoryRepository, Depends(get_history_repository)]


def get_history_service(
    history_repository: HistoryRepositoryDep,
    event_bus: EventBusDep,
) -> HistoryService:
    return HistoryService(
        history_repository=history_repository,
        event_bus=event_bus,
    )


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
