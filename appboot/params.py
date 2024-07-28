from __future__ import annotations

from inspect import Parameter, Signature
from typing import TYPE_CHECKING, Any, Callable, Optional

from fastapi import Query
from fastapi import params as fastapi_params
from pydantic.fields import FieldInfo  # noqa

from appboot._compat import ModelField, get_schema_fields
from appboot.filters import BaseFilter
from appboot.pagination import PagePagination, PaginationResult
from appboot.schema import Schema

if TYPE_CHECKING:
    from appboot.repository import Repository


def construct_query_from_field(field: ModelField) -> fastapi_params:
    return Query(
        field.field_info.default,
        default_factory=field.field_info.default_factory,
        description=field.field_info.description,
        alias=field.field_info.alias,
        title=field.field_info.title,
    )


def get_query_dependency(schema_cls: type[Schema]):
    # Create a dictionary to store the Query parameters
    query_params: list[Parameter] = []

    # Iterate over the fields of the Pydantic model
    for field_name, field in get_schema_fields(schema_cls).items():
        # Use the field default value or None if not provided
        query_params.append(
            Parameter(
                name=field_name,
                kind=Parameter.KEYWORD_ONLY,
                default=construct_query_from_field(field),
                annotation=field.annotation,
            )
        )

    # Define the dependency function
    def dependency_func(**kwargs):
        return schema_cls(**kwargs)

    # Create a new signature for the dependency function
    dependency_func.__name__ = schema_cls.__name__
    dependency_func.__signature__ = Signature(parameters=query_params)
    return dependency_func


class _QueryDepends(fastapi_params.Depends):
    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'dependency' and value:
            if issubclass(value, Schema):
                value = get_query_dependency(value)
        super().__setattr__(name, value)


def QueryDepends(  # noqa
    dependency: Optional[Callable[..., Any]] = None, *, use_cache: bool = True
) -> Any:
    return _QueryDepends(dependency, use_cache=use_cache)


class QuerySchema(BaseFilter, PagePagination):
    async def query_result(self, repository: Repository) -> PaginationResult:
        return await self.paginate(self.filter_repository(repository))
