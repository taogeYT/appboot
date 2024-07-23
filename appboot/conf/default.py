import typing

from appboot._compat import BaseModelV1, BaseSettingsV1


class EngineConfig(BaseModelV1):
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600
    echo: bool = True


class DataBases(BaseModelV1):
    default: EngineConfig


class FastAPIConfig(BaseModelV1):
    root_path: str = ''
    docs_url: typing.Optional[str] = '/docs'
    redoc_url: typing.Optional[str] = '/redoc'


class DefaultSettings(BaseSettingsV1):
    PROJECT_NAME: str = ''
    DATABASES: DataBases = DataBases(
        default=EngineConfig(url='sqlite+aiosqlite:///:memory:')
    )
    FASTAPI_CONFIG: FastAPIConfig = FastAPIConfig()

    ALLOWED_HOSTS: list[str] = []
    ALLOW_METHODS: list[str] = []
    ALLOW_HEADERS: list[str] = []
    ROOT_URLCONF: str = ''
