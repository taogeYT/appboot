from __future__ import annotations

import typing

from appboot.conf.pydantic_settings import (
    BaseSettings,
    Field,
)

DictConfig = dict[str, typing.Any]
DataBases = dict[str, DictConfig]


class DefaultSettings(BaseSettings):
    PROJECT_NAME: str = ''
    USE_TZ: bool = True
    TIME_ZONE: str = 'Asia/Shanghai'
    DATABASES: DataBases = DataBases(default=dict(url='sqlite+aiosqlite:///:memory:'))
    FASTAPI: DictConfig = Field(default_factory=dict, title='fastapi app init param')
    ALLOWED_HOSTS: list[str] = ['*']
    ALLOW_METHODS: list[str] = ['*']
    ALLOW_HEADERS: list[str] = ['*']
    ROOT_URLCONF: str = ''
    DEFAULT_TABLE_NAME_PREFIX: str = ''
