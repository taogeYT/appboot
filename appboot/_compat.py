from pydantic.version import VERSION as P_VERSION

PYDANTIC_VERSION = P_VERSION
PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")


if PYDANTIC_V2:
    from pydantic._internal._model_construction import ModelMetaclass
else:
    from pydantic.main import ModelMetaclass  # type: ignore[no-redef]

PydanticModelMetaclass = ModelMetaclass
