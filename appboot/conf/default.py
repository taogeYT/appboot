from __future__ import annotations

import typing

from appboot.conf.pydantic_settings import (
    PYDANTIC_SETTINGS_V2,
    BaseModel,
    BaseSettings,
)


class EngineConfig(BaseModel):
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600
    echo: bool = True


DataBases = dict[str, EngineConfig]


class FastAPIConfig(BaseModel):
    root_path: str = ''
    docs_url: typing.Optional[str] = '/docs'
    redoc_url: typing.Optional[str] = '/redoc'


class DefaultSettings(BaseSettings):
    if PYDANTIC_SETTINGS_V2:
        from pydantic_settings import SettingsConfigDict

        model_config = SettingsConfigDict(
            env_file='.env',
            env_file_encoding='utf-8',
            env_nested_delimiter='__',
        )
        del SettingsConfigDict
    else:

        class Config:
            env_file = '.env'
            env_file_encoding = 'utf-8'
            env_nested_delimiter = '__'

    PROJECT_NAME: str = ''
    USE_TZ: bool = True
    TIME_ZONE: str = 'Asia/Shanghai'
    DATABASES: DataBases = DataBases(
        default=EngineConfig(url='sqlite+aiosqlite:///:memory:')
    )
    FASTAPI_CONFIG: FastAPIConfig = FastAPIConfig()

    ALLOWED_HOSTS: list[str] = []
    ALLOW_METHODS: list[str] = []
    ALLOW_HEADERS: list[str] = []
    ROOT_URLCONF: str = ''
