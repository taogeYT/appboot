import typing

from pydantic import BaseModel, RedisDsn
from pydantic_core import Url
from pydantic_settings import BaseSettings


class EngineConfig(BaseSettings):
    url: Url
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600
    echo: bool = True


class DataBases(BaseModel):
    default: EngineConfig


class FastAPIConfig(BaseModel):
    root_path: str = ''
    docs_url: typing.Optional[str] = '/docs'
    redoc_url: typing.Optional[str] = '/redoc'


class DefaultSettings(BaseSettings):
    PROJECT_NAME: str = ''
    DATABASES: DataBases = DataBases(
        default=EngineConfig(url='sqlite+aiosqlite:///:memory:')
    )
    REDIS: RedisDsn = RedisDsn('redis://localhost:6379/0')
    FASTAPI_CONFIG: FastAPIConfig = FastAPIConfig()

    ALLOWED_HOSTS: list[str] = []
    ALLOW_METHODS: list[str] = []
    ALLOW_HEADERS: list[str] = []
    ROOT_URLCONF: str = ''
