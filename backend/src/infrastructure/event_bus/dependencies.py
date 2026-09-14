from typing import Annotated

from fastapi import Depends

from application.event_bus import IEventBus
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus

_event_bus: IEventBus = InMemoryEventBus()


def get_event_bus() -> IEventBus:
    return _event_bus


EventBusDep = Annotated[IEventBus, Depends(get_event_bus)]
