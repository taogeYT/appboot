from __future__ import annotations

import typing
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from typing_extensions import Self

from appboot._compat import PYDANTIC_V2, PydanticModelMetaclass
from appboot.models import Model

ModelSchemaT = typing.TypeVar('ModelSchemaT', bound='ModelSchema')
IncEx = typing.Union[
    set[int], set[str], dict[int, typing.Any], dict[str, typing.Any], None
]


def _parse_bases_fields(bases):
    base_fields = set()
    for base in bases:
        if hasattr(base, '__fields__'):
            base_fields.update(base.__fields__)
    return base_fields


def _parse_field_from_sqlalchemy_model(
    model, include=None, exclude=None, read_only_fields=None
):
    __dict__ = {}
    __annotations__ = {}
    _exclude = set() if exclude is None else set(exclude)
    _read_only_fields = set() if read_only_fields is None else set(read_only_fields)
    mapper = inspect(model)
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            column_property = attr.class_attribute
            if include and column_property.name not in include:
                continue
            if column_property.name in _exclude:
                continue
            if (
                column_property.primary_key
                or column_property.nullable
                or column_property.name in _read_only_fields
            ):
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
        meta = namespace.get('Meta')
        if meta is None or cls_name == 'ModelSchema':
            return super().__new__(mcs, cls_name, bases, namespace, **kwargs)
        namespace['Meta'] = type('Meta', (BaseMeta,), dict(meta.__dict__))
        include_fields = getattr(meta, 'fields', None)
        exclude_fields = set(getattr(meta, 'exclude', set()))
        read_only_fields = getattr(meta, 'read_only_fields', None)
        exclude_fields.add('deleted_at')
        exclude_fields.update(_parse_bases_fields(bases))
        __dict__, __annotations__ = _parse_field_from_sqlalchemy_model(
            meta.model, include_fields, exclude_fields, read_only_fields
        )
        __dict__.update(namespace)
        if '__annotations__' in namespace:
            __annotations__.update(namespace['__annotations__'])
        __dict__['__annotations__'] = __annotations__
        new_cls = super().__new__(mcs, cls_name, bases, __dict__, **kwargs)
        return new_cls


class Schema(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    else:

        class Config:
            orm_mode = True
            allow_population_by_field_name = True

    @classmethod
    def from_orm_many(cls, objs: typing.Sequence[Any]) -> list[Self]:
        return [cls.from_orm(obj) for obj in objs]

    @classmethod
    def parse_obj(cls, obj: Any) -> Self:  # noqa: D102
        if PYDANTIC_V2:
            return cls.model_validate(obj)
        else:
            return super().parse_obj(obj)

    @classmethod
    def from_orm(cls, obj: Any) -> Self:
        if PYDANTIC_V2:
            return cls.model_validate(obj)
        else:
            return super().from_orm(obj)

    def dict(
        self,
        *,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> dict[str, typing.Any]:
        if PYDANTIC_V2:
            return self.model_dump(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
        else:
            return super().dict(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )


class BaseMeta:
    model: type[Model]
    fields: typing.Sequence[str] = ()
    exclude: typing.Sequence[str] = ()
    read_only_fields: typing.Sequence[str] = ()  # pk is read only by default


class ModelSchema(Schema, metaclass=ModelSchemaMetaclass):
    Meta: typing.ClassVar[type[BaseMeta]]
