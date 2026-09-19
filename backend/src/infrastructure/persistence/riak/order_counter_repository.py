from uuid import UUID

from application.order.counter_repository import IOrderCounterRepository
from infrastructure.persistence.riak.client import RiakClient, get_riak_client


class RiakOrderCounterRepository(IOrderCounterRepository):
    """Репозиторий счетчиков заказов для Riak KV с использованием CRDT Counters."""

    def __init__(
        self,
        client: RiakClient | None = None,
        bucket: str = "order_counters",
        bucket_type: str = "counters",
        total_key: str = "__total__",
    ) -> None:
        self._client = client or get_riak_client()
        self._bucket = bucket
        self._bucket_type = bucket_type
        self._total_key = total_key

    def increment(self, user_id: UUID, amount: int = 1) -> int:
        """Инкрементировать счетчик заказов пользователя и общий счетчик."""
        user_count = self._client.counter_increment(
            bucket=self._bucket,
            key=str(user_id),
            amount=amount,
            bucket_type=self._bucket_type,
            return_body=True,
        )
        self._client.counter_increment(
            bucket=self._bucket,
            key=self._total_key,
            amount=amount,
            bucket_type=self._bucket_type,
            return_body=False,
        )
        return user_count

    def decrement(self, user_id: UUID, amount: int = 1) -> int:
        """Декрементировать счетчик заказов пользователя и общий счетчик."""
        user_count = self._client.counter_increment(
            bucket=self._bucket,
            key=str(user_id),
            amount=-amount,
            bucket_type=self._bucket_type,
            return_body=True,
        )
        self._client.counter_increment(
            bucket=self._bucket,
            key=self._total_key,
            amount=-amount,
            bucket_type=self._bucket_type,
            return_body=False,
        )
        return user_count

    def get_by_user_id(self, user_id: UUID) -> int:
        """Получить количество заказов пользователя."""
        return self._client.counter_get(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )

    def get_total_count(self) -> int:
        """Получить общее количество заказов."""
        return self._client.counter_get(
            bucket=self._bucket,
            key=self._total_key,
            bucket_type=self._bucket_type,
        )

    def delete_by_user_id(self, user_id: UUID) -> bool:
        """Удалить счетчик заказов пользователя."""
        return self._client.delete(
            bucket=self._bucket,
            key=str(user_id),
            bucket_type=self._bucket_type,
        )
