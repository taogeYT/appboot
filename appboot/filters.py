from __future__ import annotations

import functools
import typing
import warnings
from typing import Any, Callable, Optional

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
    'SearchField',
    'OrderingField',
    'BaseFilter',
)

Expression = Callable[[Base, str, Any], Any]


class BaseFieldInfo(FieldInfo):
    column_name: Optional[str]
    construct_expression: Optional[Expression]
    expression_type: typing.Literal['condition', 'ordering']

    @classmethod
    def construct_field(
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
        column_name: Optional[str] = None,
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
        field.column_name = column_name
        field.construct_expression = custom_expression
        field.expression_type = expression_type
        return field


def Field(  # noqa
    default: Any = PydanticUndefined,
    *,
    method: str | Expression = 'eq',
    column_name: Optional[str] = None,
    expression_type: typing.Literal['condition', 'ordering'] = 'condition',
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
    if not callable(method):
        custom_expression = method_table[method]
    else:
        custom_expression = method
    return BaseFieldInfo.construct_field(
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
        custom_expression=custom_expression,
        expression_type=expression_type,
        **kwargs,
    )


def equal_condition(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    if isinstance(value, (list, tuple)):
        return getattr(model, column_name).in_(value)
    return getattr(model, column_name) == value


def gt_expression(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return getattr(model, column_name) > value


def ge_expression(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return getattr(model, column_name) >= value


def lt_expression(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return getattr(model, column_name) < value


def le_expression(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return getattr(model, column_name) <= value


def contains_expression(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return getattr(model, column_name).contains(value)


def like_expression(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return getattr(model, column_name).like(value)


def startswith_expression(model, column_name, value):
    if not hasattr(model, column_name):
        raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return getattr(model, column_name).startswith(value)


def search_expression(model, column, value):
    columns = column.split(',')
    for column_name in columns:
        if not hasattr(model, column_name):
            raise FilterError(f'Model {model.__name__} has no column {column_name}')
    return or_(*[getattr(model, column).contains(value) for column in columns])


method_table = {
    'eq': equal_condition,
    'gt': gt_expression,
    'ge': ge_expression,
    'lt': lt_expression,
    'le': le_expression,
    'search': search_expression,
    'like': like_expression,
    'startswith': startswith_expression,
}


def ordering_expression(model, column, value):
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


EqField = functools.partial(Field, method=equal_condition)
GtField = functools.partial(Field, method=gt_expression)
GeField = functools.partial(Field, method=ge_expression)
LtField = functools.partial(Field, method=lt_expression)
LeField = functools.partial(Field, method=le_expression)
SearchField = functools.partial(Field, method=search_expression)
OrderingField = functools.partial(
    Field, method=ordering_expression, expression_type='ordering'
)


class BaseFilter(Schema):
    @functools.cached_property
    def filter_fields(self) -> dict[str, BaseFieldInfo]:
        model_fields = get_schema_fields(self.__class__)
        fields = {
            name: field.field_info
            for name, field in model_fields.items()
            if isinstance(field.field_info, BaseFieldInfo)
        }
        if not fields:
            warnings.warn('Filter has no filter fields')
        return fields

    def construct_condition(self, model):
        conditions = []
        for name, field in self.filter_fields.items():
            value = getattr(self, name)
            if value is not None and field.expression_type == 'condition':
                column_name = field.column_name or name
                condition = field.construct_expression(model, column_name, value)
                conditions.append(condition)
        return and_(*conditions)

    def construct_ordering(self, model):
        for name, field in self.filter_fields.items():
            if field.expression_type == 'ordering':
                value = getattr(self, name) or field.default
                return field.construct_expression(model, [], value)
        return None
