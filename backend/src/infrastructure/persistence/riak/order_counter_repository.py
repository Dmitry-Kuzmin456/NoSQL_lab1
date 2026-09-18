from uuid import UUID

from application.order.counter_repository import IOrderCounterRepository


class RiakOrderCounterRepository(IOrderCounterRepository):
    """Реализация распределенного счетчика заказов на базе Riak PN-Counter CRDT."""

    def increment(self, user_id: UUID, amount: int = 1) -> int:
        raise NotImplementedError

    def decrement(self, user_id: UUID, amount: int = 1) -> int:
        raise NotImplementedError

    def get_by_user_id(self, user_id: UUID) -> int:
        raise NotImplementedError

    def get_total_count(self) -> int:
        raise NotImplementedError

    def delete_by_user_id(self, user_id: UUID) -> bool:
        raise NotImplementedError
