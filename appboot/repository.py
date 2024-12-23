from __future__ import annotations

import typing
from typing import Any, Generic, Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Query, Session
from sqlalchemy.util import greenlet_spawn
from typing_extensions import Self

from appboot import timezone
from appboot.exceptions import DoesNotExist
from appboot.pagination import PaginationResult

if typing.TYPE_CHECKING:
    from appboot.models import Model  # noqa
    from appboot.params import QuerySchema, PaginationQuerySchema

ModelT = typing.TypeVar('ModelT', bound='Model')


class QuerySetProperty:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __get__(self, obj: typing.Optional[Model], cls: type[Model]) -> AsyncQuerySet:
        return getattr(cls, 'query_set_class', AsyncQuerySet)(
            model=cls, session=self.session_factory()
        )


class QuerySet(Query, Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: Session):
        self.model: type[ModelT] = model
        self._step: int = 1
        super().__init__(self.model, session)

    def filter_query(self, query: QuerySchema) -> Self:
        conditions = query.get_condition(self.model)
        if ordering := query.get_ordering(self.model):
            return self.order_by(*ordering).filter(conditions)
        return self.filter(conditions)

    def get_by(self, **kwargs) -> ModelT:
        result = self.filter_by(**kwargs).first()
        if result is None:
            raise DoesNotExist(f'{self.model.__name__} Not Exist')
        return result

    def _paginate(self, query: PaginationQuerySchema, must_count: bool = True):
        if must_count:
            count = self.count()
        else:
            count = 0
        results = self.limit(query.page_size).offset(query.offset).all()
        return PaginationResult(
            count=count, results=results, page=query.page, page_size=query.page_size
        )

    def paginate(
        self, query: PaginationQuerySchema, must_count: bool = True
    ) -> PaginationResult[ModelT]:
        return self.filter_query(query)._paginate(query, must_count)

    def create(self, **kwargs) -> ModelT:
        instance = self.model.construct(**kwargs)
        self.session.add(instance)
        self.session.flush([instance])
        self.session.refresh(instance)
        return instance

    def bulk_create(self, records: list[dict[str, Any]]):
        stmt = insert(self.model).values(records)
        result = self.session.execute(stmt)
        return result.rowcount


class AsyncQuerySet(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession):
        self.model: type[ModelT] = model
        self._session = session
        self._query = QuerySet(self.model, session.sync_session)
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

    def limit(self, num: int):
        self._query = self._query.limit(num)
        return self

    def offset(self, num: int):
        self._query = self._query.offset(num)
        return self

    def filter_query(self, query: QuerySchema):
        self._query = self._query.filter_query(query)
        return self

    async def paginate(
        self, query: PaginationQuerySchema, must_count: bool = True
    ) -> PaginationResult[ModelT]:
        return await greenlet_spawn(
            self._query.paginate, query=query, must_count=must_count
        )

    async def all(self) -> list[ModelT]:
        return await greenlet_spawn(self._query.all)

    async def first(self) -> Optional[ModelT]:
        return await greenlet_spawn(self._query.first)

    async def count(self) -> int:
        return await greenlet_spawn(self._query.count)

    async def get(self, **kwargs) -> ModelT:
        return await self.get_by(**kwargs)

    async def get_by(self, **kwargs) -> ModelT:
        return await greenlet_spawn(self._query.get_by, **kwargs)

    async def create(self, **kwargs) -> ModelT:
        return await greenlet_spawn(self._query.create, **kwargs)

    async def bulk_create(self, records: list[dict[str, Any]]):
        return await greenlet_spawn(self._query.bulk_create, records=records)

    async def update(
        self,
        values: dict[str, Any],
        synchronize_session='auto',
        update_args: Optional[dict[Any, Any]] = None,
    ) -> int:
        return await greenlet_spawn(
            self._query.update,
            values=values,
            synchronize_session=synchronize_session,
            update_args=update_args,
        )

    async def delete(self) -> int:
        return await greenlet_spawn(self._query.delete)

    async def values(self, *columns):
        return await greenlet_spawn(self._query.values, *columns)

    async def one(self):
        return await greenlet_spawn(self._query.one)

    async def _iter(self):
        return await greenlet_spawn(self._query._iter)

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
        return self.one()

    def __aiter__(self):
        async def generator(step):
            result = await self._iter()
            for item in result[::step]:
                yield item

        return generator(self._step)


class SoftDeleteAsyncQuerySet(AsyncQuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query = self._query.filter_by(deleted_at=None)

    async def delete(self) -> int:
        return await self.update({'deleted_at': timezone.now()})
