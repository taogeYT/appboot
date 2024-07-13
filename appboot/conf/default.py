from pydantic_core import Url
from pydantic_settings import BaseSettings
from pydantic import (
    BaseModel,
    RedisDsn
)


class EngineConfig(BaseSettings):
    url: Url
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600
    echo: bool = True


class DataBases(BaseModel):
    default: EngineConfig


class DefaultSettings(BaseSettings):
    APP_NAME: str = "app"
    DATABASES: DataBases = DataBases(default=EngineConfig(url="sqlite:///:memory:"))
    REDIS: RedisDsn = "redis://localhost:6379/0"
