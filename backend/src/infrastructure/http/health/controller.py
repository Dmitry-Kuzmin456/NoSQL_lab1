from fastapi import APIRouter, status

from infrastructure.persistence.riak.client import get_riak_client

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
    is_ok = get_riak_client().ping()
    return {
        "riak": "ok" if is_ok else "unreachable",
        "status_code": (
            status.HTTP_200_OK if is_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
    }
