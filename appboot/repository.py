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

ModelT = typing.TypeVar('ModelT', bound='Model')


class AsyncQuery(Query):
    async def async_get(self, pk: Any):
        return await greenlet_spawn(super().get, pk)

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

    async def async_values(self, *columns):
        return await greenlet_spawn(super().values, *columns)

    async def async_iter(self):
        return await greenlet_spawn(super()._iter)


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

    def get_query(self) -> AsyncQuery:
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
        obj = await self.get_query().async_get(pk)
        if not obj:
            raise DoesNotExist(f'{self.model.__name__} Not Exist')
        return obj

    async def flush(self, objects: Optional[Sequence[Any]] = None) -> None:
        return await self.session.flush(objects)

    async def bulk_create(self, instances: list[ModelT], flush=False) -> list[ModelT]:
        self.session.add_all(instances)
        if flush:
            await self.session.flush(instances)
        return instances

    async def create(self, **values: dict[str, Any]) -> ModelT:
        instance = self.model(**values)
        self.session.add(instance)
        await self.session.flush([instance])
        await self.session.refresh(instance)
        return instance

    async def update(self, **values: dict[str, Any]) -> int:
        query = self.get_query()
        if self._model_delete_condition is not None:
            query = query.filter(self._model_delete_condition)
        rowcount = await query.async_update(values)
        return rowcount

    async def delete(self) -> int:
        if self._model_delete_condition is not None:
            values = self.model.__delete_value__()  # type: ignore
            rowcount = await self.update(**values)
        else:
            rowcount = await self.get_query().async_delete()
        return rowcount


class QuerySetProperty:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __get__(self, obj: Model | None, cls: type[Model]) -> QuerySet:
        return getattr(cls, 'query_set_class', QuerySet)(
            model=cls, session=self.session_factory()
        )


class QuerySet(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession):
        self._model = model
        self._session = session
        self._query = AsyncQuery(self._model, session.sync_session)
        self._step = 1

    def options(self, *args):
        self._query = self._query.options(*args)
        return self

    def filter(self, *criterion):
        self._query = self._query.filter(*criterion)
        return self

    def filter_by(self, **kwargs):
        self._query = self._query.filter_by(**kwargs)
        return self

    def order_by(self, __first, *clauses):
        self._query = self._query.order_by(__first, *clauses)
        return self

    def distinct(self, *columns):
        self._query = self._query.distinct(*columns)
        return self

    async def all(self):
        return await self._query.async_all()

    async def first(self):
        return await self._query.async_first()

    async def count(self):
        return await self._query.async_count()

    async def get(self, **kwargs):
        result = await self._query.async_get(kwargs)
        if result is None:
            raise DoesNotExist(f'{self._model.__name__} Not Exist')
        return result

    async def create(self, **kwargs) -> ModelT:
        instance = self._model(**kwargs)
        self._query.session.add(instance)
        await self._session.flush([instance])
        await self._session.refresh(instance)
        return instance

    async def get_or_create(self, **kwargs) -> ModelT:
        instance = await self.filter_by(**kwargs).first()
        if instance is None:
            instance = await self.create(**kwargs)
        return instance

    async def update(
        self,
        values: dict[str, Any],
        synchronize_session='auto',
        update_args: Optional[dict[Any, Any]] = None,
    ):
        return await self._query.async_update(values, synchronize_session, update_args)

    async def delete(self):
        return await self._query.async_delete()

    async def values(self, *columns):
        return await self._query.async_values(*columns)

    async def iterator(self):
        return await self._query.async_iter()

    def __getitem__(self, k):
        """Retrieve an item or slice from the set of results."""
        if not isinstance(k, (int, slice)):
            raise TypeError(
                'QuerySet indices must be integers or slices, not %s.'
                % type(k).__name__
            )
        if (isinstance(k, int) and k < 0) or (
            isinstance(k, slice)
            and (
                (k.start is not None and k.start < 0)
                or (k.stop is not None and k.stop < 0)
            )
        ):
            raise ValueError('Negative indexing is not supported.')

        if isinstance(k, slice):
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            self._query = self._query.slice(start, stop)
            self._step = k.step
            return self.all()
        self._query.slice(k, k + 1)
        return self._query.async_one()

    def __aiter__(self):
        async def generator(step):
            result = await self.iterator()
            for item in result[::step]:
                yield item

        return generator(self._step)
