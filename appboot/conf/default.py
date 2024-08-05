from __future__ import annotations

import typing

from appboot.conf.pydantic_settings import (
    BaseModel,
    BaseSettings,
    Field,
)

DictConfig = dict[str, typing.Any]


class EngineConfig(BaseModel):
    url: str
    options: DictConfig = Field(
        default_factory=dict, title='sqlalchemy engine kw param'
    )


DataBases = dict[str, EngineConfig]


class DefaultSettings(BaseSettings):
    PROJECT_NAME: str = ''
    USE_TZ: bool = True
    TIME_ZONE: str = 'Asia/Shanghai'
    DATABASES: DataBases = DataBases(
        default=EngineConfig(url='sqlite+aiosqlite:///:memory:')
    )
    FASTAPI: DictConfig = Field(default_factory=dict, title='fastapi app init param')
    ALLOWED_HOSTS: list[str] = ['*']
    ALLOW_METHODS: list[str] = ['*']
    ALLOW_HEADERS: list[str] = ['*']
    ROOT_URLCONF: str = ''
    DEFAULT_TABLE_NAME_PREFIX: str = ''
