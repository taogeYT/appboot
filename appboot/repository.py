from __future__ import annotations

import typing
from typing import Any, Generic, Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Query
from sqlalchemy.util import greenlet_spawn

from appboot import timezone
from appboot.exceptions import DoesNotExist
from appboot.pagination import PaginationResult

if typing.TYPE_CHECKING:
    from appboot.models import Model  # noqa
    from appboot.params import QuerySchema, PaginationQuerySchema

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

    @property
    def model(self) -> type[ModelT]:
        return self._model

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

    def limit(self, num: int):
        self._query = self._query.limit(num)
        return self

    def offset(self, num: int):
        self._query = self._query.offset(num)
        return self

    def filter_query(self, query: QuerySchema):
        conditions = query.get_condition(self.model)
        if ordering := query.get_ordering(self.model):
            return self.order_by(*ordering).filter(conditions)
        return self.filter(conditions)

    async def _paginate(self, query: PaginationQuerySchema, must_count: bool = True):
        if must_count:
            count = await self.count()
        else:
            count = 0
        results = await self.limit(query.page_size).offset(query.offset).all()
        return PaginationResult(
            count=count, results=results, page=query.page, page_size=query.page_size
        )

    async def paginate(self, query: PaginationQuerySchema, must_count: bool = True) -> PaginationResult[ModelT]:
        return await self.filter_query(query)._paginate(query, must_count)

    async def all(self) -> list[ModelT]:
        return await self._query.async_all()

    async def first(self) -> Optional[ModelT]:
        return await self._query.async_first()

    async def count(self) -> int:
        return await self._query.async_count()

    async def get(self, **kwargs) -> ModelT:
        result = await self.filter_by(**kwargs).first()
        if result is None:
            raise DoesNotExist(f'{self._model.__name__} Not Exist')
        return result

    async def create(self, **kwargs) -> ModelT:
        # todo 支持关联关系一同创建
        instance = self._model(
            **{k: v for k, v in kwargs.items() if k in self.model.__mapper__.columns}
        )
        self._query.session.add(instance)
        await self._session.flush([instance])
        await self._session.refresh(instance)
        return instance

    async def bulk_create(self, records: list[dict[str, Any]]):
        stmt = insert(self.model).values(records)
        result = await self._session.execute(stmt)
        return result.rowcount

    async def update(
        self,
        values: dict[str, Any],
        synchronize_session='auto',
        update_args: Optional[dict[Any, Any]] = None,
    ) -> int:
        return await self._query.async_update(values, synchronize_session, update_args)

    async def delete(self) -> int:
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


class SoftDeleteQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query = self._query.filter_by(deleted_at=None)

    async def delete(self) -> int:
        return await self.update({'deleted_at': timezone.now()})
