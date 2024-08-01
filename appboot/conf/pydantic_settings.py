from appboot._compat import PYDANTIC_V2

PYDANTIC_SETTINGS_V2 = False
if PYDANTIC_V2:
    try:
        from pydantic import BaseModel as BaseModel
        from pydantic._internal._model_construction import ModelMetaclass  # noqa
        from pydantic_settings import BaseSettings as PydanticSettings

        PYDANTIC_SETTINGS_V2 = True
    except ImportError:
        from pydantic.v1 import BaseModel  # type: ignore
        from pydantic.v1.env_settings import BaseSettings as PydanticSettings
        from pydantic.v1.main import ModelMetaclass as ModelMetaclass
else:
    from pydantic import BaseModel as BaseModel
    from pydantic import BaseSettings as PydanticSettings  # type: ignore
    from pydantic.main import ModelMetaclass as ModelMetaclass  # type: ignore

__all__ = (
    'BaseModel',
    'BaseSettings',
    'ModelMetaclass',
)


class BaseSettings(PydanticSettings):
    # if PYDANTIC_SETTINGS_V2:
    #     from pydantic_settings import SettingsConfigDict
    #
    #     model_config = SettingsConfigDict(
    #         env_file='.env',
    #         env_file_encoding='utf-8',
    #         env_nested_delimiter='__',
    #     )
    #     del SettingsConfigDict
    # else:
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'
