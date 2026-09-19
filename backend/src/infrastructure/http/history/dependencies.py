from typing import Annotated

from fastapi import Depends

from application.history.repository import IHistoryRepository
from application.history.service import HistoryService
from infrastructure.event_bus.dependencies import get_event_bus
from infrastructure.persistence.composite.history_repository import (
    CompositeHistoryRepository,
)
from infrastructure.persistence.postgres.history_repository import (
    PostgresHistoryRepository,
)
from infrastructure.persistence.riak.history_cache_repository import (
    RiakHistoryCacheRepository,
)

_postgres_history_repository: PostgresHistoryRepository = PostgresHistoryRepository()
_riak_history_cache_repository: RiakHistoryCacheRepository = (
    RiakHistoryCacheRepository()
)
_history_repository: IHistoryRepository = CompositeHistoryRepository(
    postgres_repo=_postgres_history_repository,
    riak_repo=_riak_history_cache_repository,
)


def get_postgres_history_repository() -> PostgresHistoryRepository:
    return _postgres_history_repository


def get_riak_history_cache_repository() -> RiakHistoryCacheRepository:
    return _riak_history_cache_repository


def get_history_repository() -> IHistoryRepository:
    return _history_repository


HistoryRepositoryDep = Annotated[IHistoryRepository, Depends(get_history_repository)]


_history_service: HistoryService = HistoryService(
    history_repository=_history_repository,
    event_bus=get_event_bus(),
)


def get_history_service() -> HistoryService:
    return _history_service


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
