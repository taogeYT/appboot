import datetime
import typing
from typing import Generic, Optional, Type

from sqlalchemy import select
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio.session import AsyncSession

from appboot.model import SchemaT

RepositoryT = typing.TypeVar('RepositoryT', bound='Repository')


class Repository(Generic[SchemaT]):
    schema: Type[SchemaT]

    def __init__(self, schema: Type[SchemaT], session: AsyncSession):
        self.schema = schema
        self.model = schema.Meta.model
        self.order_by = self.model.id.desc()
        self.where = []
        self.kw_where = {}
        self.slice = 0, 10000
        self.option_alive = True
        self.session = session

    def reset(self):
        self.where = []
        self.kw_where = {}
        self.slice = 0, 10000
        # self.option_alive = True

    def disable_option(self):
        self.option_alive = False
        return self

    def get_option(self):
        _deleted_at_condition = self.model.deleted_at.is_(None)
        return with_loader_criteria(self.model, _deleted_at_condition)

    def filter(self, *condition):
        self.where.extend(condition)
        return self

    def filter_by(self, **kwargs):
        self.kw_where.update(kwargs)
        return self

    def limit(self, limit, offset=0):
        self.slice = (offset, limit)
        return self

    def clone(self):
        return self.__class__(self.schema)

    def get_query(self):
        stmt = select(self.model)
        if self.kw_where:
            stmt = stmt.filter_by(**self.kw_where)
        if self.where:
            stmt = stmt.where(*self.where)
        if self.option_alive:
            stmt = stmt.options(self.get_option())
        stmt = stmt.order_by(self.order_by).slice(*self.slice)
        # self.reset()
        return stmt

    async def all(self) -> list[SchemaT]:
        stmt = self.get_query()
        result = await self.session.scalars(stmt)
        return [self.schema.model_validate(obj) for obj in result]

    async def first(self) -> Optional[SchemaT]:
        stmt = self.get_query()
        obj = await self.session.scalar(stmt)
        return self.schema.model_validate(obj) if obj else None

    async def get(self, pk: int) -> Optional[SchemaT]:
        return await self.filter_by(id=pk).first()

    async def mget(self, pks: list[int]) -> dict[int, SchemaT]:
        objs = await self.filter(self.model.id.in_(pks)).all()
        return {obj.id: obj for obj in objs}

    async def bulk_create(self, objs: list[SchemaT], flush=False) -> list[SchemaT]:
        instances = [self.model(**obj.dict(exclude_defaults=True)) for obj in objs]
        self.session.add_all(instances)
        if flush:
            await self.session.flush()
        return [self.schema.model_validate(ins) for ins in instances]

    async def create(self, obj: SchemaT, flush=False) -> SchemaT:
        instance = self.model(**obj.dict(exclude_defaults=True))
        self.session.add(instance)
        if flush:
            await self.session.flush()
        return self.schema.model_validate(instance)

    async def update(self, obj: SchemaT, flush=False) -> SchemaT:
        if not obj.id:
            raise ValueError()
        instance = await self.get(obj.id)
        self.session.add(instance)
        if flush:
            await self.session.flush()
        return self.schema.model_validate(instance)

    async def delete(self, obj: SchemaT, flush=False) -> SchemaT:
        if not obj.id:
            raise ValueError()
        instance = await self.get(obj.id)
        instance.deleted_at = datetime.datetime.now()
        if flush:
            await self.session.flush()
        return self.schema.model_validate(instance)
