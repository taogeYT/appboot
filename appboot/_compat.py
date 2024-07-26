from pydantic.version import VERSION as P_VERSION

PYDANTIC_VERSION = P_VERSION
PYDANTIC_V2 = PYDANTIC_VERSION.startswith('2.')


if PYDANTIC_V2:
    from pydantic._internal._model_construction import ModelMetaclass  # noqa
    from pydantic.fields import PydanticUndefined as PydanticUndefined  # noqa
else:
    from pydantic.fields import Undefined  # noqa
    from pydantic.main import ModelMetaclass  # noqa

    PydanticUndefined = Undefined

PydanticModelMetaclass = ModelMetaclass


def get_schema_fields(schema):
    if PYDANTIC_V2:
        return schema.model_fields
    else:
        return schema.__fields__
