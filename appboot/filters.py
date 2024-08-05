from __future__ import annotations

import typing
from typing import Any, Callable, Iterable, Optional

from pydantic.fields import FieldInfo  # noqa
from sqlalchemy import and_, asc, desc

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


class BaseFieldInfo(FieldInfo):
    def construct_expression(self, model, columns, value):
        pass


class QueryFieldInfo(BaseFieldInfo):
    @property
    def columns(self) -> Optional[typing.Iterable[str]]:
        return getattr(self, '_columns', None)

    @columns.setter
    def columns(self, value):
        setattr(self, '_columns', value)


class EqFieldInfo(QueryFieldInfo):
    def construct_expression(self, model, columns, value):
        return equal_construct_condition(model, columns[0], value)


def construct_field(
    field_cls: type[QueryFieldInfo],
    default: Any = PydanticUndefined,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    columns: Optional[str | typing.Sequence[str]] = None,
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
    field.columns = [columns] if isinstance(columns, str) else columns
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
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    columns: Optional[str | typing.Sequence[str]] = None,
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
        columns=columns,
        **kwargs,
    )


class GtFieldInfo(QueryFieldInfo):
    def construct_expression(self, model, columns, value):
        return getattr(model, columns[0]) > value


def GtField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    columns: Optional[str | typing.Sequence[str]] = None,
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
        columns=columns,
        **kwargs,
    )


class GeFieldInfo(QueryFieldInfo):
    def construct_expression(self, model, columns, value):
        return getattr(model, columns[0]) >= value


def GeField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    columns: Optional[str | typing.Sequence[str]] = None,
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
        columns=columns,
        **kwargs,
    )


class LtFieldInfo(QueryFieldInfo):
    def construct_expression(self, model, columns, value):
        return getattr(model, columns[0]) < value


def LtField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    columns: Optional[str | typing.Sequence[str]] = None,
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
        columns=columns,
        **kwargs,
    )


class LeFieldInfo(QueryFieldInfo):
    def construct_expression(self, model, columns, value):
        return getattr(model, columns[0]) <= value


def LeField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    columns: Optional[str | typing.Sequence[str]] = None,
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
        columns=columns,
        **kwargs,
    )


class ContainsFieldInfo(QueryFieldInfo):
    def construct_expression(self, model, columns, value):
        return getattr(model, columns[0]).contains(value)


def ContainsField(  # noqa
    default: Optional[Any] = None,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    columns: Optional[str | typing.Sequence[str]] = None,
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
        columns=columns,
        **kwargs,
    )


class SearchFieldInfo(BaseFieldInfo):
    def construct_expression(self, model, columns, value):
        raise NotImplementedError


class OrderingFieldInfo(BaseFieldInfo):
    def construct_expression(self, model, columns, value):
        if not isinstance(value, str):
            raise FilterError('OrderingField must be an instance of str')
        values = value.split(',')
        orderings = []
        for name in values:
            _func = asc
            if name.startswith('-'):
                name = name[1:]
                _func = desc
            if not hasattr(model, name):
                raise FilterError(f'Model {model.__name__} has no sort column {name}')
            orderings.append(_func(getattr(model, name)))
        return orderings


def OrderingField(  # noqa
    default: str,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Optional[Any] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    ge: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    **kwargs: Any,
) -> Any:
    return OrderingFieldInfo(
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


class BaseFilter(Schema):
    def filter_repository(self, repository: Repository) -> Repository:
        conditions = self.get_condition(repository.model)
        if ordering := self.get_ordering(repository.model):
            return repository.order_by(*ordering).filter(conditions)
        return repository.filter(conditions)

    def get_condition(self, model):
        conditions = []
        model_fields = get_schema_fields(self.__class__)
        for name, field in model_fields.items():
            field_info = field.field_info
            value = getattr(self, name)
            if value is None:
                continue
            if not isinstance(field_info, QueryFieldInfo):
                continue
            columns = field_info.columns or [name]
            for column_name in columns:
                if not hasattr(model, column_name):
                    raise FilterError(
                        f'Model {model.__name__} has no column {column_name}'
                    )
            condition = field_info.construct_expression(model, columns, value)
            conditions.append(condition)
        return and_(*conditions)

    def get_ordering(self, model):
        model_fields = get_schema_fields(self.__class__)
        for name, field in model_fields.items():
            field_info = field.field_info
            if isinstance(field_info, OrderingFieldInfo):
                value = getattr(self, name) or field_info.default
                return field_info.construct_expression(model, [], value)
        return None
