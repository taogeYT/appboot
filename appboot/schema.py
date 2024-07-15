import sys
import typing

from pydantic import Field
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty

from appboot._compat import PYDANTIC_V2, PydanticModelMetaclass
from appboot.models import BaseSchema, Model, ModelT
from appboot.repository import Repository, RepositoryT

ModelSchemaT = typing.TypeVar("ModelSchemaT", bound="ModelSchema")

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = typing.TypeVar("Self", bound="ModelSchema")


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
            __dict__[column_property.name] = Field(default, title=column_property.doc)
    return __dict__, __annotations__


class ModelSchemaMetaclass(PydanticModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: tuple[type[typing.Any], ...],
        namespace: dict[str, typing.Any],
        **kwargs: typing.Any,
    ) -> type:
        meta = namespace.get("Meta")
        if meta is None or cls_name == "ModelSchema":
            return super().__new__(mcs, cls_name, bases, namespace, **kwargs)
        if not hasattr(meta, "repository_class"):
            meta.repository_class = Repository
        include_fields = getattr(meta, "include_fields", None)
        exclude_fields = set(getattr(meta, "exclude_fields", set()))
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
        setattr(new_cls, "objects", RepositoryDescriptor(meta.repository_class))
        return new_cls


class RepositoryDescriptor:
    def __init__(self, repository_class):
        self.repository_class = repository_class

    def __get__(self, instance, cls):
        return self.repository_class(cls)


class BaseMeta(object):
    model: type[ModelT] = Model  # type: ignore
    include_fields: typing.Sequence = []
    exclude_fields: typing.Sequence = []
    repository_class: type[RepositoryT] = Repository  # type: ignore


class ModelSchema(BaseSchema, metaclass=ModelSchemaMetaclass):
    Meta: typing.ClassVar[BaseMeta] = BaseMeta()
    objects: typing.ClassVar[Repository[Self]]  # type: ignore

    async def save(self, flush: bool = False) -> Self:
        if self.id:
            obj = await self.objects.update(self, flush)
        else:
            obj = await self.objects.create(self, flush)
        return obj

    async def delete(self, flush: bool = False) -> Self:
        return await self.objects.delete(self, flush)

    @classmethod
    def from_sqlalchemy_model(cls: type[Self], instance: ModelT) -> Self:
        # exclude _sa_instance_state
        data = {
            name: v for name, v in instance.__dict__.items() if not name.startswith("_")
        }
        if PYDANTIC_V2:
            obj = cls.model_validate(data)
        else:
            obj = cls.parse_obj(data)
        obj._instance = instance
        return obj
