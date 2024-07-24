from appboot._compat import PYDANTIC_V2

PYDANTIC_SETTINGS_V2 = False
if PYDANTIC_V2:
    try:
        from pydantic import BaseModel  # noqa
        from pydantic._internal._model_construction import ModelMetaclass  # noqa
        from pydantic_settings import BaseSettings

        PYDANTIC_SETTINGS_V2 = True
    except ImportError:  # type: ignore[unused-ignore]
        from pydantic.v1 import BaseModel, BaseSettings  # type: ignore
        from pydantic.v1.main import ModelMetaclass
else:
    from pydantic import BaseModel, BaseSettings  # type: ignore
    from pydantic.main import ModelMetaclass  # type: ignore

__all__ = (
    'PYDANTIC_SETTINGS_V2',
    'BaseModel',
    'BaseSettings',
    'ModelMetaclass',
)
