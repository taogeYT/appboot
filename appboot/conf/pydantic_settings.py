from appboot._compat import PYDANTIC_V2

PYDANTIC_SETTINGS_V2 = False
if PYDANTIC_V2:
    try:
        from pydantic import BaseModel as BaseModel
        from pydantic import Field as Field
        from pydantic._internal._model_construction import ModelMetaclass  # noqa
        from pydantic_settings import BaseSettings as PydanticSettings

        PYDANTIC_SETTINGS_V2 = True
    except ImportError:
        from pydantic.v1 import BaseModel, Field  # type: ignore
        from pydantic.v1.env_settings import BaseSettings as PydanticSettings
        from pydantic.v1.main import ModelMetaclass as ModelMetaclass
else:
    from pydantic import BaseModel as BaseModel
    from pydantic import BaseSettings as PydanticSettings  # type: ignore
    from pydantic import Field as Field
    from pydantic.main import ModelMetaclass as ModelMetaclass  # type: ignore

__all__ = (
    'Field',
    'BaseModel',
    'BaseSettings',
    'ModelMetaclass',
)


class BaseSettings(PydanticSettings):
    class Config:
        extra = 'ignore'
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return env_settings, file_secret_settings, init_settings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return env_settings, dotenv_settings, file_secret_settings, init_settings
