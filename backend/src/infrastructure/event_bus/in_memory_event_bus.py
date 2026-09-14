import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar

from application.event_bus import EventHandler, IEventBus

logger = logging.getLogger(__name__)

T = TypeVar("T")


class InMemoryEventBus(IEventBus):
    """In-memory реализация шины событий с потокобезопасным диспетчером."""

    def __init__(self) -> None:
        self._handlers: dict[type[Any], list[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type: type[T], handler: EventHandler[T]) -> None:
        with self._lock:
            handlers_list = self._handlers[event_type]
            if handler not in handlers_list:
                handlers_list.append(handler)

    def publish(self, event: Any) -> None:
        event_type = type(event)
        with self._lock:
            matched_handlers: list[Callable[[Any], None]] = []
            for registered_type, handlers in self._handlers.items():
                if issubclass(event_type, registered_type):
                    matched_handlers.extend(handlers)

        for handler in matched_handlers:
            try:
                handler(event)
            except Exception:
                handler_name = getattr(handler, "__qualname__", repr(handler))
                logger.exception(
                    "Ошибка при обработке события '%s' обработчиком '%s'",
                    event_type.__name__,
                    handler_name,
                )
