import logging
from dataclasses import dataclass
from typing import Any

import httpx

from infrastructure.environment.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RiakObject:
    bucket: str
    key: str
    data: Any
    bucket_type: str
    vclock: str | None


def _build_kv_url(bucket: str, key: str, bucket_type: str = "default") -> str:
    return f"/types/{bucket_type}/buckets/{bucket}/keys/{key}"


def _build_datatype_url(bucket: str, key: str, bucket_type: str) -> str:
    return f"/types/{bucket_type}/buckets/{bucket}/datatypes/{key}"


class RiakClient:
    """HTTP-клиент для Riak KV."""

    def __init__(self) -> None:
        self.base_url = settings.riak.base_url.rstrip("/")
        self.timeout = settings.riak.timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Accept": "application/json, */*"},
        )

    def close(self) -> None:
        self._client.close()

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        try:
            response = self._client.request(method, url, **kwargs)
            if response.status_code != 404:
                response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            logger.error("Riak error [%s %s]: %s", method, url, exc)
            raise

    def ping(self) -> bool:
        try:
            response = self._client.get("/ping")
            return response.status_code == 200 and response.text.strip() == "OK"
        except httpx.RequestError as exc:
            logger.warning("Riak ping failed: %s", exc)
            return False

    def get(
        self,
        bucket: str,
        key: str,
        bucket_type: str = "default",
    ) -> RiakObject | None:
        url = _build_kv_url(bucket, key, bucket_type)
        response = self._request("GET", url)
        if response.status_code == 404:
            return None

        return RiakObject(
            bucket=bucket,
            key=key,
            data=response.json(),
            bucket_type=bucket_type,
            vclock=response.headers.get("x-riak-vclock"),
        )

    def put(self, obj: RiakObject) -> RiakObject:
        url = _build_kv_url(obj.bucket, obj.key, obj.bucket_type)
        headers: dict[str, str] = {"Content-Type": "application/json"}

        if obj.vclock:
            headers["X-Riak-Vclock"] = obj.vclock

        response = self._request(
            "PUT",
            url,
            json=obj.data,
            headers=headers,
        )
        returned_vclock = response.headers.get("x-riak-vclock", obj.vclock)
        return RiakObject(
            bucket=obj.bucket,
            key=obj.key,
            data=obj.data,
            bucket_type=obj.bucket_type,
            vclock=returned_vclock,
        )

    def delete(self, bucket: str, key: str, bucket_type: str = "default") -> bool:
        url = _build_kv_url(bucket, key, bucket_type)
        response = self._request("DELETE", url)
        return response.status_code in (204, 404) or response.is_success

    def counter_increment(
        self,
        bucket: str,
        key: str,
        amount: int = 1,
        bucket_type: str = "counters",
    ) -> int:
        url = _build_datatype_url(bucket, key, bucket_type)
        self._request(
            "POST",
            url,
            json={"increment": amount},
            headers={"Content-Type": "application/json"},
        )
        return self.counter_get(bucket, key, bucket_type)

    def counter_get(
        self,
        bucket: str,
        key: str,
        bucket_type: str = "counters",
    ) -> int:
        url = _build_datatype_url(bucket, key, bucket_type)
        response = self._request("GET", url)
        if response.status_code == 404:
            return 0
        return int(response.json().get("value", 0))

    def set_add(
        self,
        bucket: str,
        key: str,
        elements: str | list[str],
        bucket_type: str = "sets",
    ) -> set[str]:
        url = _build_datatype_url(bucket, key, bucket_type)
        payload = (
            {"add": elements} if isinstance(elements, str) else {"add_all": elements}
        )
        self._request(
            "POST",
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        return self.set_get(bucket, key, bucket_type)

    def set_remove(
        self,
        bucket: str,
        key: str,
        elements: str | list[str],
        bucket_type: str = "sets",
    ) -> set[str]:
        url = _build_datatype_url(bucket, key, bucket_type)
        payload = (
            {"remove": elements}
            if isinstance(elements, str)
            else {"remove_all": elements}
        )
        self._request(
            "POST",
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        return self.set_get(bucket, key, bucket_type)

    def set_get(
        self,
        bucket: str,
        key: str,
        bucket_type: str = "sets",
    ) -> set[str]:
        url = _build_datatype_url(bucket, key, bucket_type)
        response = self._request("GET", url)
        if response.status_code == 404:
            return set()
        return set(response.json().get("value", []))

    def map_update(
        self,
        bucket: str,
        key: str,
        update_spec: dict[str, Any],
        bucket_type: str = "maps",
    ) -> dict[str, Any]:
        url = _build_datatype_url(bucket, key, bucket_type)
        self._request(
            "POST",
            url,
            json={"update": update_spec},
            headers={"Content-Type": "application/json"},
        )
        return self.map_get(bucket, key, bucket_type) or {}

    def map_get(
        self,
        bucket: str,
        key: str,
        bucket_type: str = "maps",
    ) -> dict[str, Any] | None:
        url = _build_datatype_url(bucket, key, bucket_type)
        response = self._request("GET", url)
        if response.status_code == 404:
            return None
        return response.json().get("value", {})


_client = RiakClient()


def get_riak_client() -> RiakClient:
    return _client


def close_riak_client() -> None:
    _client.close()
