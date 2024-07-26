from __future__ import annotations

import typing
import warnings
from inspect import Parameter, Signature
from typing import Any, Callable, Iterable, Optional

from fastapi import Query, params
from pydantic.fields import FieldInfo  # noqa
from sqlalchemy import and_

from appboot._compat import PydanticUndefined, get_schema_fields
from appboot.schema import Schema

if typing.TYPE_CHECKING:
    from appboot.repository import Repository


__all__ = (
    'Field',
    'EqField',
    'GeField',
    'GtField',
    'LeField',
    'LtField',
    'ContainsField',
    'FilterSchema',
    'FilterDepends',
)


def equal_construct_condition(model, name, value):
    if isinstance(value, Iterable):
        return getattr(model, name).in_(value)
    return getattr(model, name) == value


def construct_query_from_field(field: FieldInfo) -> params.Query:
    return Query(
        field.default,
        default_factory=field.default_factory,
        description=field.description,
        alias=field.alias,
        title=field.title,
    )


class QueryFieldInfo(FieldInfo):
    def construct_condition(self, model, name, value):
        pass


class EqFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return equal_construct_condition(model, name, value)


def EqField(  # noqa
    default: Any = PydanticUndefined,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    discriminator: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return EqFieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        discriminator=discriminator,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs,
    )


Field = EqField


class GtFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) > value


def GtField(  # noqa
    default: Any = PydanticUndefined,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    discriminator: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return GtFieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        discriminator=discriminator,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs,
    )


class GeFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) >= value


def GeField(  # noqa
    default: Any = PydanticUndefined,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    discriminator: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return GeFieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        discriminator=discriminator,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs,
    )


class LtFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) < value


def LtField(  # noqa
    default: Any = PydanticUndefined,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    discriminator: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return LtFieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        discriminator=discriminator,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs,
    )


class LeFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name) <= value


def LeField(  # noqa
    default: Any = PydanticUndefined,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    discriminator: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return LeFieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        discriminator=discriminator,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs,
    )


class ContainsFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        return getattr(model, name).contains(value)


def ContainsField(  # noqa
    default: Any = PydanticUndefined,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    discriminator: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    return ContainsFieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        discriminator=discriminator,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        **kwargs,
    )


class SearchFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        raise NotImplementedError


class OrderingFieldInfo(QueryFieldInfo):
    def construct_condition(self, model, name, value):
        raise NotImplementedError


class FilterSchema(Schema):
    def filter(self, repository: Repository):
        conditions = self.construct_expression(repository.model)
        return repository.filter(conditions)

    def construct_expression(self, model):
        conditions = []
        model_fields = get_schema_fields(self)
        for name, field in model_fields.items():
            value = getattr(self, name)
            if value is None:
                continue
            if not hasattr(model, name):
                warnings.warn(
                    f'{self.__class__.__name__}.{name} not found in [{model.__name__}] Model'
                )
                continue
            if isinstance(field, FieldInfo):
                condition = equal_construct_condition(model, name, value)
            elif isinstance(field, QueryFieldInfo):
                condition = field.construct_condition(model, name, value)
            else:
                raise NotImplementedError
            print(condition, name, value)
            conditions.append(condition)
        return and_(*conditions)


def get_filter_dependency(filter_schema_cls: type[FilterSchema]):
    # Create a dictionary to store the Query parameters
    query_params: list[Parameter] = []

    # Iterate over the fields of the Pydantic model
    for field_name, field in get_schema_fields(filter_schema_cls).items():
        # Use the field default value or None if not provided
        query_params.append(
            Parameter(
                name=field_name,
                kind=Parameter.KEYWORD_ONLY,
                default=construct_query_from_field(field),
                annotation=field.annotation,  # todo compat v1
            )
        )

    # Define the dependency function
    def dependency_func(**kwargs):
        return filter_schema_cls(**kwargs)

    # Create a new signature for the dependency function
    dependency_func.__name__ = filter_schema_cls.__name__
    dependency_func.__signature__ = Signature(parameters=query_params)  # type: ignore
    return dependency_func


class _FilterDepends(params.Depends):
    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'dependency' and value:
            if issubclass(value, FilterSchema):
                value = get_filter_dependency(value)
        super().__setattr__(name, value)


def FilterDepends(  # noqa
    dependency: Optional[Callable[..., Any]] = None, *, use_cache: bool = True
) -> Any:
    return _FilterDepends(dependency, use_cache=use_cache)
