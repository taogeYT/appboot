import datetime
import typing
from typing import Generic, Optional, Sequence

from pydantic import BaseModel, Field
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from appboot.db import Base, ScopedSession
from appboot.exceptions import DoesNotExist
from appboot.interfaces import BaseRepository

ModelT = typing.TypeVar("ModelT", bound=Base)


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
        if self._model is None:
            self._query = _Query(order_by=None)
        else:
            mapper = inspect(model)
            if mapper is None or not mapper.is_mapper:
                raise ValueError("Expected mapped class or mapper, got: %r" % model)
            self._query = _Query(order_by=mapper.primary_key)
            if self.model.__deleted_at_option__:
                self.options(self.model.__deleted_at_option__)

    def __get__(self, instance, cls):
        if instance is None:
            return self.__class__(cls)
        raise ValueError("Repository cannot be accessed through instance")

    @property
    def model(self) -> type[ModelT]:
        if self._model is None:
            raise ValueError("Model is not set")
        return self._model

    @property
    def session(self) -> AsyncSession:
        return ScopedSession()

    def disable_option(self):
        self._query.option_alive = False
        return self

    def filter(self, *condition):
        self._query.where.extend(condition)
        return self

    def filter_by(self, **kwargs):
        self._query.kw_where.update(kwargs)
        return self

    def limit(self, num: int):
        self._query.limit = num
        return self

    def offset(self, num: int):
        self._query.offset = num
        return self

    def slice(self, start: int, end: int):
        self._query.offset = start
        self._query.limit = end - start
        return self

    def options(self, *args):
        self._query.with_options += args
        return self

    def order_by(self, *args):
        self._query.order_by = args
        return self

    def get_query(self):
        stmt = select(self.model)
        if self._query.kw_where:
            stmt = stmt.filter_by(**self._query.kw_where)
        if self._query.where:
            stmt = stmt.where(*self._query.where)
        stmt = stmt.options(*self._query.get_options())
        stmt = (
            stmt.limit(self._query.limit)
            .offset(self._query.offset)
            .order_by(*self._query.order_by)
        )
        return stmt

    async def all(self) -> Sequence[ModelT]:
        stmt = self.get_query()
        result = await self.session.scalars(stmt)
        return result.all()

    async def first(self) -> Optional[ModelT]:
        stmt = self.get_query()
        obj = await self.session.scalar(stmt)
        return obj

    async def get(self, pk: typing.Any) -> ModelT:
        obj = await self.session.get(self.model, pk, options=self._query.get_options())
        if not obj:
            raise DoesNotExist(f"{self.model.__name__}.{pk}")
        return obj

    async def bulk_create(self, objs: list[BaseModel], flush=False) -> list[ModelT]:
        instances = [self.model(**obj.dict(exclude_defaults=True)) for obj in objs]
        self.session.add_all(instances)
        if flush:
            await self.session.flush()
        return instances

    async def create(self, obj: BaseModel, flush=False) -> ModelT:
        instance = self.model(**obj.dict(exclude_defaults=True))
        self.session.add(instance)
        if flush:
            await self.session.flush()
        return instance

    async def update(self, pk: int, obj: BaseModel, flush=False) -> ModelT:
        instance = await self.get(pk)
        for name, value in obj.dict(exclude={"id"}).items():
            if hasattr(instance, name) and getattr(instance, name) != value:
                setattr(instance, name, value)
        if flush:
            await self.session.flush()
        return instance

    async def delete(self, pk: int, flush=False) -> ModelT:
        instance = await self.get(pk)
        if self.model.__deleted_at_option__ and hasattr(instance, "deleted_at"):
            instance.deleted_at = datetime.datetime.now()
        else:
            await self.session.delete(instance)
        if flush:
            await self.session.flush()
        return instance
