import json
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
    content_type: str
    vclock: str | None
    indexes: dict[str, str | int]


def _build_kv_url(bucket: str, key: str, bucket_type: str = "default") -> str:
    return f"/types/{bucket_type}/buckets/{bucket}/keys/{key}"


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
        try:
            response = self._client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()

            content_type = response.headers.get("content-type", "application/json")
            vclock = response.headers.get("x-riak-vclock")

            indexes: dict[str, str | int] = {}
            for header_name, header_value in response.headers.items():
                if header_name.lower().startswith("x-riak-index-"):
                    indexes[header_name[13:]] = header_value

            if "application/json" in content_type:
                try:
                    data = response.json()
                except ValueError:
                    data = response.text
            else:
                data = response.text

            return RiakObject(
                bucket=bucket,
                key=key,
                data=data,
                bucket_type=bucket_type,
                content_type=content_type,
                vclock=vclock,
                indexes=indexes,
            )
        except httpx.RequestError as exc:
            logger.error("Riak get error (%s/%s): %s", bucket, key, exc)
            raise

    def put(
        self,
        bucket: str,
        key: str,
        data: Any,
        bucket_type: str = "default",
        content_type: str = "application/json",
        vclock: str | None = None,
        indexes: dict[str, str | int] | None = None,
    ) -> RiakObject:
        url = _build_kv_url(bucket, key, bucket_type)
        headers: dict[str, str] = {"Content-Type": content_type}

        if vclock:
            headers["X-Riak-Vclock"] = vclock

        if indexes:
            for idx_name, idx_val in indexes.items():
                headers[f"x-riak-index-{idx_name}"] = str(idx_val)

        if content_type == "application/json" and not isinstance(data, (str, bytes)):
            body = json.dumps(data)
        elif isinstance(data, str):
            body = data
        else:
            body = json.dumps(data)

        try:
            response = self._client.put(url, content=body, headers=headers)
            response.raise_for_status()
            returned_vclock = response.headers.get("x-riak-vclock", vclock)
            return RiakObject(
                bucket=bucket,
                key=key,
                data=data,
                bucket_type=bucket_type,
                content_type=content_type,
                vclock=returned_vclock,
                indexes=indexes or {},
            )
        except httpx.RequestError as exc:
            logger.error("Riak put error (%s/%s): %s", bucket, key, exc)
            raise

    def delete(self, bucket: str, key: str, bucket_type: str = "default") -> bool:
        url = _build_kv_url(bucket, key, bucket_type)
        try:
            response = self._client.delete(url)
            if response.status_code in (204, 404):
                return True
            response.raise_for_status()
            return True
        except httpx.RequestError as exc:
            logger.error("Riak delete error (%s/%s): %s", bucket, key, exc)
            raise

    def query_index_exact(
        self,
        bucket: str,
        index_name: str,
        value: str | int,
        bucket_type: str = "default",
    ) -> list[str]:
        if bucket_type and bucket_type != "default":
            url = f"/types/{bucket_type}/buckets/{bucket}/index/{index_name}/{value}"
        else:
            url = f"/buckets/{bucket}/index/{index_name}/{value}"

        try:
            response = self._client.get(url)
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json().get("keys", [])
        except httpx.RequestError as exc:
            logger.error("Riak 2i error (%s/%s): %s", bucket, index_name, exc)
            raise

    def query_index_range(
        self,
        bucket: str,
        index_name: str,
        start_val: str | int,
        end_val: str | int,
        bucket_type: str = "default",
    ) -> list[str]:
        if bucket_type and bucket_type != "default":
            url = f"/types/{bucket_type}/buckets/{bucket}/index/{index_name}/{start_val}/{end_val}"
        else:
            url = f"/buckets/{bucket}/index/{index_name}/{start_val}/{end_val}"

        try:
            response = self._client.get(url)
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return response.json().get("keys", [])
        except httpx.RequestError as exc:
            logger.error("Riak 2i range error (%s/%s): %s", bucket, index_name, exc)
            raise

    def _build_datatype_url(self, bucket: str, key: str, bucket_type: str) -> str:
        return f"/types/{bucket_type}/buckets/{bucket}/datatypes/{key}"

    def counter_increment(
        self,
        bucket: str,
        key: str,
        amount: int = 1,
        bucket_type: str = "counters",
    ) -> int:
        url = self._build_datatype_url(bucket, key, bucket_type)
        try:
            response = self._client.post(
                url,
                json={"increment": amount},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return self.counter_get(bucket, key, bucket_type)
        except httpx.RequestError as exc:
            logger.error("Riak counter error (%s/%s): %s", bucket, key, exc)
            raise

    def counter_get(
        self,
        bucket: str,
        key: str,
        bucket_type: str = "counters",
    ) -> int:
        url = self._build_datatype_url(bucket, key, bucket_type)
        try:
            response = self._client.get(url)
            if response.status_code == 404:
                return 0
            response.raise_for_status()
            return int(response.json().get("value", 0))
        except httpx.RequestError as exc:
            logger.error("Riak counter get error (%s/%s): %s", bucket, key, exc)
            raise

    def set_add(
        self,
        bucket: str,
        key: str,
        elements: str | list[str],
        bucket_type: str = "sets",
    ) -> set[str]:
        url = self._build_datatype_url(bucket, key, bucket_type)
        payload = (
            {"add": elements} if isinstance(elements, str) else {"add_all": elements}
        )
        try:
            response = self._client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return self.set_get(bucket, key, bucket_type)
        except httpx.RequestError as exc:
            logger.error("Riak set add error (%s/%s): %s", bucket, key, exc)
            raise

    def set_remove(
        self,
        bucket: str,
        key: str,
        elements: str | list[str],
        bucket_type: str = "sets",
    ) -> set[str]:
        url = self._build_datatype_url(bucket, key, bucket_type)
        payload = (
            {"remove": elements}
            if isinstance(elements, str)
            else {"remove_all": elements}
        )
        try:
            response = self._client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return self.set_get(bucket, key, bucket_type)
        except httpx.RequestError as exc:
            logger.error("Riak set remove error (%s/%s): %s", bucket, key, exc)
            raise

    def set_get(
        self,
        bucket: str,
        key: str,
        bucket_type: str = "sets",
    ) -> set[str]:
        url = self._build_datatype_url(bucket, key, bucket_type)
        try:
            response = self._client.get(url)
            if response.status_code == 404:
                return set()
            response.raise_for_status()
            return set(response.json().get("value", []))
        except httpx.RequestError as exc:
            logger.error("Riak set get error (%s/%s): %s", bucket, key, exc)
            raise

    def map_update(
        self,
        bucket: str,
        key: str,
        update_spec: dict[str, Any],
        bucket_type: str = "maps",
    ) -> dict[str, Any]:
        url = self._build_datatype_url(bucket, key, bucket_type)
        try:
            response = self._client.post(
                url,
                json={"update": update_spec},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return self.map_get(bucket, key, bucket_type) or {}
        except httpx.RequestError as exc:
            logger.error("Riak map update error (%s/%s): %s", bucket, key, exc)
            raise

    def map_get(
        self,
        bucket: str,
        key: str,
        bucket_type: str = "maps",
    ) -> dict[str, Any] | None:
        url = self._build_datatype_url(bucket, key, bucket_type)
        try:
            response = self._client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json().get("value", {})
        except httpx.RequestError as exc:
            logger.error("Riak map get error (%s/%s): %s", bucket, key, exc)
            raise


_client = RiakClient()


def get_riak_client() -> RiakClient:
    return _client


def close_riak_client() -> None:
    _client.close()
