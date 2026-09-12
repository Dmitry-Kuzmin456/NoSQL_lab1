import httpx
from fastapi import APIRouter, status

from infrastructure.environment.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    summary="Общий статус доступности приложения",
    status_code=status.HTTP_200_OK,
)
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/riak",
    summary="Проверка доступности Riak KV",
    status_code=status.HTTP_200_OK,
)
def riak_health() -> dict[str, str | int]:
    url = f"{settings.riak.base_url.rstrip('/')}/ping"
    try:
        response = httpx.get(url, timeout=5.0)
    except httpx.RequestError as exc:
        return {"riak": "unreachable", "detail": str(exc)}
    return {
        "riak": "ok" if response.status_code == 200 else "error",
        "status_code": response.status_code,
    }
