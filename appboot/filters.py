from __future__ import annotations

import typing
from typing import Any, Callable, Iterable, Optional

from pydantic.fields import FieldInfo  # noqa
from sqlalchemy import and_

from appboot._compat import PydanticUndefined, get_schema_fields
from appboot.exceptions import FilterError
from appboot.schema import Schema

if typing.TYPE_CHECKING:
    from appboot.repository import Repository


__all__ = (
    'EqField',
    'GeField',
    'GtField',
    'LeField',
    'LtField',
    'ContainsField',
    'BaseFilter',
)


def equal_construct_condition(model, name, value):
    if isinstance(value, Iterable):
        return getattr(model, name).in_(value)
    return getattr(model, name) == value


class QueryFieldInfo(FieldInfo):
    @property
    def column_name(self) -> Optional[str]:
        return getattr(self, '_column_name', None)

    @column_name.setter
    def column_name(self, value):
        setattr(self, '_column_name', value)

    def construct_condition(self, model, name, value):
        pass


class EqFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return equal_construct_condition(model, name, value)


def construct_field(
    field_cls: type[QueryFieldInfo],
    default: Any = PydanticUndefined,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[str] = None,
    max_length: Optional[str] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    column_name: Optional[str] = None,
    **kwargs: Any,
):
    field = field_cls(
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        exclude=exclude,
        min_length=min_length,
        max_length=max_length,
        gt=gt,
        lt=lt,
        ge=ge,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs,
    )
    field.column_name = column_name
    return field


def EqField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[str] = None,
    max_length: Optional[str] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    column_name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return construct_field(
        field_cls=EqFieldInfo,
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        exclude=exclude,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        column_name=column_name,
        **kwargs,
    )


class GtFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) > value


def GtField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[str] = None,
    max_length: Optional[str] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    column_name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return construct_field(
        field_cls=GtFieldInfo,
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        exclude=exclude,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        column_name=column_name,
        **kwargs,
    )


class GeFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) >= value


def GeField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[str] = None,
    max_length: Optional[str] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    column_name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return construct_field(
        field_cls=GeFieldInfo,
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        exclude=exclude,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        column_name=column_name,
        **kwargs,
    )


class LtFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) < value


def LtField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[str] = None,
    max_length: Optional[str] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    column_name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return construct_field(
        field_cls=LtFieldInfo,
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        exclude=exclude,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        column_name=column_name,
        **kwargs,
    )


class LeFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) <= value


def LeField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[str] = None,
    max_length: Optional[str] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    column_name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return construct_field(
        field_cls=LeFieldInfo,
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        exclude=exclude,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        column_name=column_name,
        **kwargs,
    )


class ContainsFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name).contains(value)


def ContainsField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[str] = None,
    max_length: Optional[str] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    column_name: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return construct_field(
        field_cls=ContainsFieldInfo,
        default=default,
        default_factory=default_factory,
        alias=alias,
        alias_priority=alias_priority,
        title=title,
        description=description,
        exclude=exclude,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        column_name=column_name,
        **kwargs,
    )


class SearchFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        raise NotImplementedError


class OrderingFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        raise NotImplementedError


class BaseFilter(Schema):
    def filter_repository(self, repository: Repository) -> Repository:
        conditions = self.get_condition(repository.model)
        return repository.filter(conditions)

    def get_condition(self, model):
        conditions = []
        model_fields = get_schema_fields(self)
        for name, field in model_fields.items():
            value = getattr(self, name)
            if value is None:
                continue
            if not isinstance(field, QueryFieldInfo):
                continue
            column_name = field.column_name or name
            if not hasattr(model, column_name):
                raise FilterError(f'Model {model.__name__} has no column {column_name}')
            condition = field.construct_condition(model, column_name, value)
            conditions.append(condition)
        return and_(*conditions)
