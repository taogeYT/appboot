from dataclasses import dataclass
from typing import Any

from pydantic.version import VERSION as P_VERSION

PYDANTIC_VERSION = P_VERSION
PYDANTIC_V2 = PYDANTIC_VERSION.startswith('2.')


if PYDANTIC_V2:
    from pydantic._internal._model_construction import ModelMetaclass  # noqa
    from pydantic.fields import PydanticUndefined as PydanticUndefined  # noqa
    from pydantic.fields import FieldInfo

    @dataclass
    class ModelField:
        field_info: FieldInfo
        name: str

        @property
        def type_(self) -> Any:
            return self.field_info.annotation

        @property
        def annotation(self):
            return self.field_info.annotation
else:
    from pydantic.fields import Undefined  # noqa
    from pydantic.main import ModelMetaclass  # noqa
    from pydantic.fields import ModelField  # noqa

    PydanticUndefined = Undefined

PydanticModelMetaclass = ModelMetaclass


def get_schema_fields(schema) -> dict[str, ModelField]:
    if PYDANTIC_V2:
        return {
            k: ModelField(field_info=v, name=k) for k, v in schema.model_fields.items()
        }
    else:
        return schema.__fields__
