from uuid import UUID

from application.event_bus import IEventBus
from domain.history import OperationEvent

from .dto import UserHistoryResponseDto
from .repository import IHistoryRepository


class HistoryService:
    """Сервис истории действий пользователей."""

    def __init__(
        self,
        history_repository: IHistoryRepository,
        event_bus: IEventBus,
    ) -> None:
        self._history_repository = history_repository
        event_bus.subscribe(OperationEvent, self.handle_event)

    def handle_event(self, event: OperationEvent) -> None:
        """Обработчик события из шины событий."""
        self.record_event(event)

    def record_event(self, event: OperationEvent) -> None:
        """Зафиксировать событие в истории."""
        self._history_repository.add_event(event)

    def get_by_user_id(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> UserHistoryResponseDto:
        """Получить историю действий пользователя с пагинацией."""
        events, total = self._history_repository.get_user_events(
            user_id=user_id,
            offset=offset,
            limit=limit,
        )
        return UserHistoryResponseDto.from_events(
            user_id=user_id,
            events=events,
            total=total,
            offset=offset,
            limit=limit,
        )

    def clear_user_history(self, user_id: UUID) -> bool:
        """Очистить историю действий пользователя."""
        return self._history_repository.clear(user_id)
