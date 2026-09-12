import httpx
from fastapi import FastAPI
from infrastructure.environment.settings import settings

app = FastAPI(title="Our site")

RIAK_HTTP_URL = settings.riak.base_url


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/riak")
def riak_health() -> dict[str, str | int]:
    url = f"{RIAK_HTTP_URL.rstrip('/')}/ping"
    try:
        response = httpx.get(url, timeout=5.0)
    except httpx.RequestError as exc:
        return {"riak": "unreachable", "detail": str(exc)}
    return {
        "riak": "ok" if response.status_code == 200 else "error",
        "status_code": response.status_code,
    }
