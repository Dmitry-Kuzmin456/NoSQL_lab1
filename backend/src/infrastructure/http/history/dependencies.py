from typing import Annotated

from fastapi import Depends

from application.history.repository import IHistoryRepository
from application.history.service import HistoryService
from infrastructure.event_bus.dependencies import get_event_bus
from infrastructure.persistence.in_memory.history_repository import (
    InMemoryHistoryRepository,
)

_history_repository: IHistoryRepository = InMemoryHistoryRepository()
_history_service: HistoryService = HistoryService(
    history_repository=_history_repository,
    event_bus=get_event_bus(),
)


def get_history_repository() -> IHistoryRepository:
    return _history_repository


def get_history_service() -> HistoryService:
    return _history_service


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
