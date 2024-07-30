from __future__ import annotations

import typing
from functools import cached_property
from typing import Any, Generic, Optional, Sequence

from pydantic import BaseModel, Field
from sqlalchemy import Column, inspect
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import LoaderCriteriaOption, Query, with_loader_criteria
from sqlalchemy.util import greenlet_spawn

from appboot.db import ScopedSession
from appboot.exceptions import DoesNotExist
from appboot.interfaces import BaseRepository

if typing.TYPE_CHECKING:
    from appboot.models import Model  # noqa
    from appboot.schema import Schema

ModelT = typing.TypeVar('ModelT', bound='Model')


class AsyncQuery(Query):
    async def async_count(self) -> int:
        return await greenlet_spawn(super().count)

    async def async_all(self):
        return await greenlet_spawn(super().all)

    async def async_first(self):
        return await greenlet_spawn(super().first)

    async def async_one_or_none(self):
        return await greenlet_spawn(super().one_or_none)

    async def async_one(self):
        return await greenlet_spawn(super().one)

    async def async_delete(self, synchronize_session='auto'):
        return await greenlet_spawn(
            super().delete, synchronize_session=synchronize_session
        )

    async def async_update(
        self,
        values: dict[str, Any],
        synchronize_session='auto',
        update_args: Optional[dict[Any, Any]] = None,
    ):
        return await greenlet_spawn(
            super().update,
            values=values,
            synchronize_session=synchronize_session,
            update_args=update_args,
        )


class _Query(BaseModel):
    order_by: typing.Any
    where: list[typing.Any] = Field(default_factory=list)
    kw_where: dict[str, typing.Any] = Field(default_factory=dict)
    limit: int = 10000
    offset: int = 0
    option_alive: bool = True
    with_options: tuple[typing.Any, ...] = ()

    def get_options(self):
        if self.option_alive:
            return self.with_options
        return ()


class Repository(BaseRepository[ModelT], Generic[ModelT]):
    def __init__(self, model: Optional[type[ModelT]] = None):
        self._model = model
        if self._model is not None:
            mapper = inspect(model)
            if mapper is None or not mapper.is_mapper:
                raise ValueError('Expected mapped class or mapper, got: %r' % model)
            self._primary_key = mapper.primary_key
            self._query = AsyncQuery(self.model, self.session.sync_session)

    def __get__(self, instance, cls):
        if instance is None:
            return self.__class__(cls)
        raise ValueError('Repository cannot be accessed through instance')

    @property
    def model(self) -> type[ModelT]:
        if self._model is None:
            raise ValueError('Model is not set')
        return self._model

    @property
    def primary_key(self) -> tuple[Column[Any], ...]:
        return self._primary_key

    @property
    def session(self) -> AsyncSession:
        return ScopedSession()

    def filter(self, *condition):
        self._query = self._query.filter(*condition)
        return self

    def filter_by(self, **kwargs):
        self._query = self._query.filter_by(**kwargs)
        return self

    def limit(self, num: int):
        self._query = self._query.limit(num)
        return self

    def offset(self, num: int):
        self._query = self._query.offset(num)
        return self

    def slice(self, start: int, end: int):
        self._query = self._query.slice(start, end)
        return self

    def options(self, *args):
        self._query = self._query.options(*args)
        return self

    def order_by(self, *args):
        self._query = self._query.order_by(*args)
        return self

    def group_by(self, __first, *clauses):
        self._query = self._query.group_by(__first, *clauses)
        return self

    def having(self, *having):
        self._query = self._query.having(*having)
        return self

    def join(
        self,
        target: Any,
        onclause: Optional[Any] = None,
        *,
        isouter: bool = False,
        full: bool = False,
    ):
        self._query = self._query.join(target, onclause, isouter=isouter, full=full)
        return self

    def with_for_update(
        self,
        *,
        nowait: bool = False,
        read: bool = False,
        of: Optional[Any] = None,
        skip_locked: bool = False,
        key_share: bool = False,
    ):
        self._query = self._query.with_for_update(
            nowait=nowait,
            read=read,
            of=of,
            skip_locked=skip_locked,
            key_share=key_share,
        )
        return self

    def with_entities(self, *entities: Any, **__kw: Any):
        self._query = self._query.with_entities(*entities, **__kw)
        return self

    def clone(self) -> Repository:
        r = self.__class__(self.model)
        r._query = self._query
        return r

    async def _fetch_all(self) -> Sequence[ModelT]:
        return await self.get_query().async_all()

    def __aiter__(self):
        async def generator():
            result = await self._fetch_all()
            for item in result:
                yield item

        return generator()

    @cached_property
    def _delete_options(self) -> typing.Sequence[LoaderCriteriaOption]:
        if self._model_delete_condition is not None:
            return [with_loader_criteria(self.model, self._model_delete_condition)]
        return []

    @cached_property
    def _model_delete_condition(self):
        if hasattr(self.model, '__delete_condition__'):
            return self.model.__delete_condition__()
        return None

    def get_query(self):
        if self._delete_options:
            return self._query.options(*self._delete_options)
        return self._query

    @property
    def statement(self):
        return self.get_query().statement

    async def count(self) -> int:
        return await self.get_query().async_count()

    async def all(self) -> Sequence[ModelT]:
        return await self._fetch_all()

    async def first(self) -> Optional[ModelT]:
        obj = await self.session.scalar(self.statement)
        return obj

    async def get(self, pk: typing.Any) -> ModelT:
        obj = await self.session.get(self.model, pk, options=self._delete_options)
        if not obj:
            raise DoesNotExist(f'{self.model.__name__} Not Exist')
        return obj

    def _model_dump_for_write(self, obj: Schema | dict[str, Any]) -> dict[str, Any]:
        if isinstance(obj, dict):
            return obj
        read_only_fields = set(c.name for c in self.primary_key)
        if hasattr(obj, 'Meta') and hasattr(obj.Meta, 'read_only_fields'):
            read_only_fields |= set(obj.Meta.read_only_fields)
        return obj.dict(exclude=read_only_fields, exclude_unset=True)

    async def bulk_create(self, objs: list[Schema], flush=False) -> list[ModelT]:
        instances = [self.model(**self._model_dump_for_write(obj)) for obj in objs]
        self.session.add_all(instances)
        if flush:
            await self.session.flush(instances)
        return instances

    async def create(self, obj: Schema | dict[str, Any], flush=False) -> ModelT:
        instance = self.model(**self._model_dump_for_write(obj))
        self.session.add(instance)
        if flush:
            await self.session.flush([instance])
            await self.session.refresh(instance)
        return instance

    async def update(self, values: Schema | dict[str, Any]) -> int:
        query = self.get_query()
        if self._model_delete_condition is not None:
            query = query.filter(self._model_delete_condition)
        rowcount = await query.async_update(self._model_dump_for_write(values))
        return rowcount

    async def update_one(
        self, pk: int, obj: Schema | dict[str, Any], flush=False
    ) -> ModelT:
        instance = await self.get(pk)
        instance.update(**self._model_dump_for_write(obj))
        if flush:
            await self.session.flush([instance])
        return instance

    async def delete_one(self, pk: int, flush=False) -> ModelT:
        instance = await self.get(pk)
        if hasattr(self.model, '__delete_value__'):
            values = self.model.__delete_value__()  # type: ignore
            instance.update(**values)
        else:
            await self.session.delete(instance)
        if flush:
            await self.session.flush([instance])
        return instance
