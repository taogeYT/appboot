import datetime
import typing
from typing import Generic, Optional, Sequence

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import with_loader_criteria

from appboot.db import ScopedSession
from appboot.exceptions import DoesNotExist
from appboot.interfaces import BaseRepository
from appboot.models import ModelT

RepositoryT = typing.TypeVar("RepositoryT", bound="Repository")


class _Query(BaseModel):
    order_by: typing.Any
    where: list[typing.Any] = Field(default_factory=list)
    kw_where: dict[str, typing.Any] = Field(default_factory=dict)
    limit: int = 10000
    offset: int = 0
    option_alive: bool = True


class Repository(BaseRepository[ModelT], Generic[ModelT]):
    def __init__(self, model: Optional[type[ModelT]] = None):
        self._model = model
        if self._model is None:
            self._query = _Query(order_by=None)
        else:
            self._query = _Query(order_by=self.model.id.desc())

    def __get__(self, instance, cls):
        if instance is None:
            return self.__class__(cls)
        raise AttributeError("instance is not yet assigned")

    @property
    def model(self) -> type[ModelT]:
        if self._model is None:
            raise AttributeError("model is not set")
        return self._model

    @property
    def session(self) -> AsyncSession:
        return ScopedSession()

    def disable_option(self):
        self._query.option_alive = False
        return self

    def get_option(self):
        _deleted_at_condition = self.model.deleted_at.is_(None)
        return with_loader_criteria(self.model, _deleted_at_condition)

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

    def get_query(self):
        stmt = select(self.model)
        if self._query.kw_where:
            stmt = stmt.filter_by(**self._query.kw_where)
        if self._query.where:
            stmt = stmt.where(*self._query.where)
        if self._query.option_alive:
            stmt = stmt.options(self.get_option())
        stmt = (
            stmt.limit(self._query.limit)
            .offset(self._query.offset)
            .order_by(self._query.order_by)
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

    async def get(self, pk: int) -> ModelT:
        obj = await self.filter_by(id=pk).first()
        if not obj:
            raise DoesNotExist(f"{self.model.__name__}.{pk}")
        return obj

    async def mget(self, pks: list[int]) -> dict[int, ModelT]:
        objs = await self.filter(self.model.id.in_(pks)).all()
        return {obj.id: obj for obj in objs}

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
        for name, value in obj.dict(exclude={"id", "created_at", "updated_at"}).items():
            if hasattr(instance, name) and getattr(instance, name) != value:
                setattr(instance, name, value)
        if flush:
            await self.session.flush()
        return instance

    async def delete(self, pk: int, flush=False) -> ModelT:
        instance = await self.get(pk)
        instance.deleted_at = datetime.datetime.now()
        if flush:
            await self.session.flush()
        return instance
