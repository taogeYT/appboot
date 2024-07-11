import sys
import typing

from pydantic import Field
from pydantic._internal._model_construction import ModelMetaclass
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from appboot.model import ModelT, Model, BaseSchema
from appboot.repository import Repository, RepositoryT

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = typing.TypeVar('Self', bound='ModelSchema')


def _parse_field_from_sqlalchemy_model(model, attrs):
    __annotations__ = {}
    mapper = inspect(model)
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            column_property = attr.class_attribute
            if column_property.nullable:
                python_type = typing.Optional[column_property.type.python_type]
                default = None
            else:
                python_type = column_property.type.python_type
                default = ...
            __annotations__[column_property.name] = python_type
            attrs[column_property.name] = Field(default, title=column_property.doc)
    if "__annotations__" in attrs:
        attrs["__annotations__"].update(__annotations__)
    else:
        attrs["__annotations__"] = __annotations__


class ModelSchemaMetaclass(ModelMetaclass):
    def __new__(
            mcs,
            cls_name: str,
            bases: tuple[type[typing.Any], ...],
            namespace: dict[str, typing.Any],
            **kwargs: typing.Any
    ) -> type:
        # meta = namespace.pop('Meta', None)
        if cls_name == 'ModelSchema':
            return super().__new__(mcs, cls_name, bases, namespace, **kwargs)
        meta = namespace['Meta']
        if hasattr(meta, "fields"):
            pass
        if not hasattr(meta, "repository_class"):
            meta.repository_class = Repository
        _parse_field_from_sqlalchemy_model(meta.model, namespace)
        new_cls = super().__new__(mcs, cls_name, bases, namespace, **kwargs)
        new_cls.objects = RepositoryDescriptor(meta.repository_class)
        return new_cls


class RepositoryDescriptor:

    def __init__(self, repository_class):
        self.repository_class = repository_class

    def __get__(self, instance, cls):
        return self.repository_class(cls)


class BaseMeta:
    model: typing.Type[ModelT] = Model
    fields: typing.Iterable = []
    repository_class: typing.Type[RepositoryT] = Repository


class ModelSchema(BaseSchema, metaclass=ModelSchemaMetaclass):
    Meta: typing.ClassVar[BaseMeta] = BaseMeta()
    objects: typing.ClassVar[Repository[Self]]

    async def save(self, flush=False):
        if self.id:
            obj = await self.objects.create(self, flush)
        else:
            obj = await self.objects.update(self, flush)
        return obj

    async def delete(self, flush=False):
        return await self.objects.delete(self, flush)
