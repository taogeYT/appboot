from __future__ import annotations

import functools
import typing
from typing import Any, Callable, Optional, Sequence

from pydantic.fields import FieldInfo  # noqa
from sqlalchemy import and_, asc, desc, or_

from appboot._compat import PydanticUndefined, get_schema_fields
from appboot.db import Base
from appboot.exceptions import FilterError
from appboot.schema import Schema

__all__ = (
    'EqField',
    'GeField',
    'GtField',
    'LeField',
    'LtField',
    'ContainsField',
    'SearchField',
    'OrderingField',
    'BaseFilter',
)

Expression = Callable[[Base, Sequence[str], Any], Any]


class BaseFieldInfo(FieldInfo):
    construct_expression: Optional[Expression]
    expression_type: typing.Literal['condition', 'ordering']
    columns: Optional[typing.Iterable[str]]

    @classmethod
    def construct_filter_field(
        cls,
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
        custom_expression: Optional[Expression] = None,
        expression_type: typing.Literal['condition', 'ordering'] = 'condition',
        **kwargs: Any,
    ):
        field = cls(
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
        field.construct_expression = custom_expression
        field.expression_type = expression_type
        return field


def Field(  # noqa
    default: Any = PydanticUndefined,
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
    custom_expression: Optional[Expression] = None,
    expression_type: typing.Literal['condition', 'ordering'] = 'condition',
    **kwargs: Any,
) -> Any:
    return BaseFieldInfo.construct_filter_field(
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
        custom_expression=custom_expression,
        expression_type=expression_type,
        **kwargs,
    )


def equal_condition(model, columns, value):
    if isinstance(value, (list, tuple)):
        return getattr(model, columns[0]).in_(value)
    return getattr(model, columns[0]) == value


def gt_expression(model, columns, value):
    return getattr(model, columns[0]) > value


def ge_expression(model, columns, value):
    return getattr(model, columns[0]) >= value


def lt_expression(model, columns, value):
    return getattr(model, columns[0]) < value


def le_expression(model, columns, value):
    return getattr(model, columns[0]) <= value


def contains_expression(model, columns, value):
    return getattr(model, columns[0]).contains(value)


def search_expression(model, columns, value):
    return or_(*[getattr(model, column).contains(value) for column in columns])


def ordering_expression(model, columns, value):
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


EqField = functools.partial(Field, custom_expression=equal_condition)
GtField = functools.partial(Field, custom_expression=gt_expression)
GeField = functools.partial(Field, custom_expression=ge_expression)
LtField = functools.partial(Field, custom_expression=lt_expression)
LeField = functools.partial(Field, custom_expression=le_expression)
ContainsField = functools.partial(Field, custom_expression=contains_expression)
SearchField = functools.partial(Field, custom_expression=search_expression)
OrderingField = functools.partial(
    Field, custom_expression=ordering_expression, expression_type='ordering'
)


class BaseFilter(Schema):
    def construct_condition(self, model):
        conditions = []
        model_fields = get_schema_fields(self.__class__)
        for name, field in model_fields.items():
            field_info = field.field_info
            value = getattr(self, name)
            if value is None:
                continue
            if (
                isinstance(field_info, BaseFieldInfo)
                and field_info.expression_type == 'condition'
            ):
                columns = field_info.columns or [name]
                for column_name in columns:
                    if not hasattr(model, column_name):
                        raise FilterError(
                            f'Model {model.__name__} has no column {column_name}'
                        )
                condition = field_info.construct_expression(model, columns, value)
                conditions.append(condition)
        return and_(*conditions)

    def construct_ordering(self, model):
        model_fields = get_schema_fields(self.__class__)
        for name, field in model_fields.items():
            field_info = field.field_info
            if (
                isinstance(field_info, BaseFieldInfo)
                and field_info.expression_type == 'ordering'
            ):
                value = getattr(self, name) or field_info.default
                return field_info.construct_expression(model, [], value)
        return None
