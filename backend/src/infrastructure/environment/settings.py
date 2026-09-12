from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class RiakSettings(BaseModel):
    base_url: str = "http://localhost:8087"


class AuthSettings(BaseModel):
    jwt_secret_key: str = "dev-secret-key-change-in-production-32bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cookie_secure: bool = False
    cookie_httponly: bool = True
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"


class Settings(BaseSettings):
    riak: RiakSettings = RiakSettings()
    auth: AuthSettings = AuthSettings()

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_nested_delimiter="__",
        extra="ignore",
    )


# noinspection PyArgumentList
settings = Settings()
