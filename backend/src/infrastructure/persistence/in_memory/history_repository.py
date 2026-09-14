import copy
import threading
from collections import defaultdict
from uuid import UUID

from application.history.repository import IHistoryRepository
from domain.history import OperationEvent


class InMemoryHistoryRepository(IHistoryRepository):
    """In-memory хранилище истории пользователей по модели Append-Only."""

    def __init__(self, max_history_size: int = 100) -> None:
        self._user_events: dict[UUID, list[OperationEvent]] = defaultdict(list)
        self._max_history_size = max_history_size
        self._lock = threading.RLock()

    def add_event(self, event: OperationEvent) -> None:
        """Атомарно добавляет событие в начало списка без вычитки всех данных."""
        with self._lock:
            events = self._user_events[event.user_id]
            events.insert(0, copy.deepcopy(event))
            if len(events) > self._max_history_size:
                del events[self._max_history_size :]

    def get_user_events(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[OperationEvent], int]:
        """Возвращает срез событий с пагинацией и общее число событий пользователя."""
        with self._lock:
            events = self._user_events.get(user_id, [])
            total = len(events)
            paginated = events[offset : offset + limit]
            return [copy.deepcopy(e) for e in paginated], total

    def count_user_events(self, user_id: UUID) -> int:
        """Быстро получить общее количество событий пользователя без вычитки всех записей."""
        with self._lock:
            return len(self._user_events.get(user_id, []))

    def exists_by_user_id(self, user_id: UUID) -> bool:
        """Проверить наличие хотя бы одного события у пользователя."""
        with self._lock:
            return bool(self._user_events.get(user_id))

    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удаляет всю историю пользователя."""
        with self._lock:
            if user_id in self._user_events:
                del self._user_events[user_id]
                return True
            return False
