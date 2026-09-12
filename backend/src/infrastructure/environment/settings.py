from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class RiakSettings(BaseModel):
    base_url: str


class Settings(BaseSettings):
    riak: RiakSettings

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_nested_delimiter="__",
    )


# noinspection PyArgumentList
settings = Settings()
