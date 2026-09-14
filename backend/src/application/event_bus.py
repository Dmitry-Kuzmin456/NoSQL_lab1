from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
EventHandler = Callable[[T], None]


class IEventBus(ABC):
    """Интерфейс шины событий (Event Bus)."""

    @abstractmethod
    def publish(self, event: Any) -> None:
        """Опубликовать событие для зарегистрированных обработчиков."""
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: type[T], handler: EventHandler[T]) -> None:
        """Подписать обработчик на определенный тип событий."""
        raise NotImplementedError
