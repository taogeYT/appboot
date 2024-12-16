from __future__ import annotations

import typing

from pydantic import Field
from sqlalchemy import inspect

from appboot._compat import PydanticModelMetaclass, get_schema_fields
from appboot.base import Schema
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
    for column_property in mapper.columns:
        if include and column_property.name not in include:
            continue
        if column_property.name in _exclude:
            continue
        if column_property.primary_key or column_property.name in _read_only_fields:
            read_only = True
        else:
            read_only = False
        if (
            column_property.primary_key
            or column_property.nullable
            or column_property.name in _read_only_fields
        ):
            python_type = typing.Optional[column_property.type.python_type]
            default = None
        else:
            if column_property.default:
                if column_property.default.is_scalar:
                    python_type = column_property.type.python_type
                    default = column_property.default.arg
                else:
                    python_type = typing.Optional[column_property.type.python_type]
                    default = None
            else:
                python_type = column_property.type.python_type
                default = ...
        __annotations__[column_property.name] = python_type
        __dict__[column_property.name] = Field(
            default,
            title=column_property.doc or column_property.name,
            read_only=read_only,
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


class BaseMeta:
    model: type[Model]
    fields: typing.Sequence[str] = ()
    exclude: typing.Sequence[str] = ()
    read_only_fields: typing.Sequence[str] = ()  # pk is read only by default


class ModelSchema(Schema, metaclass=ModelSchemaMetaclass):
    Meta: typing.ClassVar[type[BaseMeta]]

    @classmethod
    def construct_schema(cls, **kwargs):
        fields = get_schema_fields(cls)
        return cls(**{k: v for k, v in kwargs if k in fields})

    @property
    def validated_data(self):
        fields = get_schema_fields(self.__class__)
        include = set()
        for name, field in fields.items():
            json_schema_extra = field.field_info.json_schema_extra
            if json_schema_extra and json_schema_extra.get('read_only'):
                continue
            include.add(name)
        return self.dict(include=include, exclude_unset=True)

    async def create(self, **kwargs):
        kwargs.update(self.validated_data)
        instance = await self.Meta.model.objects.create(**kwargs)
        return instance

    async def update(self, instance: Model, **values):
        values.update(self.validated_data)
        for name, value in values.items():
            if name in instance.__mapper__.columns and getattr(instance, name) != value:
                setattr(instance, name, value)
        await instance.save()
        return instance
