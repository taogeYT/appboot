import typing

from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty

from appboot._compat import PydanticModelMetaclass
from appboot.db import Base
from appboot.repository import Repository

ModelSchemaT = typing.TypeVar("ModelSchemaT", bound="ModelSchema")


def clone_model(
    name: str, base: type[BaseModel], exclude_fields: set[str]
) -> type[BaseModel]:
    original_fields: dict[str, typing.Any] = base.model_fields
    new_fields: dict[str, typing.Any] = {
        name: (field.annotation, field.default)
        for name, field in original_fields.items()
        if name not in exclude_fields
    }

    new_model = create_model(name, __config__=base.model_config, **new_fields)
    return new_model


def _parse_bases_fields(bases):
    base_fields = set()
    for base in bases:
        if hasattr(base, "__fields__"):
            base_fields.update(base.__fields__)
    return base_fields


def _parse_field_from_sqlalchemy_model(model, include=None, exclude=None):
    __dict__ = {}
    __annotations__ = {}
    _exclude = set() if exclude is None else set(exclude)
    mapper = inspect(model)
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            column_property = attr.class_attribute
            if include and column_property.name not in include:
                continue
            if column_property.name in _exclude:
                continue
            if column_property.nullable:
                python_type = typing.Optional[column_property.type.python_type]
                default = None
            else:
                python_type = column_property.type.python_type
                default = ...
            __annotations__[column_property.name] = python_type
            __dict__[column_property.name] = Field(
                default, title=column_property.doc or column_property.name
            )
    return __dict__, __annotations__


class ModelSchemaMetaclass(PydanticModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: tuple[type[typing.Any], ...],
        namespace: dict[str, typing.Any],
        **kwargs: typing.Any,
    ) -> type:
        if cls_name == "ModelSchema":
            return super().__new__(mcs, cls_name, bases, namespace, **kwargs)
        meta = namespace.get("Meta")
        if meta is None:
            raise ValueError("'Meta' is required for ModelSchema")
        if not hasattr(meta, "repository_class"):
            meta.repository_class = Repository
        include_fields = getattr(meta, "fields", None)
        exclude_fields = set(getattr(meta, "exclude", set()))
        exclude_fields.add("deleted_at")
        exclude_fields.update(_parse_bases_fields(bases))
        __dict__, __annotations__ = _parse_field_from_sqlalchemy_model(
            meta.model, include_fields, exclude_fields
        )
        __dict__.update(namespace)
        if "__annotations__" in namespace:
            __annotations__.update(namespace["__annotations__"])
        __dict__["__annotations__"] = __annotations__
        new_cls = super().__new__(mcs, cls_name, bases, __dict__, **kwargs)
        return new_cls


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseMeta:
    model: type[Base] = Base
    fields: typing.Sequence[str] = []
    exclude: typing.Sequence[str] = []
    read_only_fields: typing.Sequence[str] = []  # pk is read only by default


class ModelSchema(Schema, metaclass=ModelSchemaMetaclass):
    Meta: typing.ClassVar[type[BaseMeta]]
