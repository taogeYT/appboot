from __future__ import annotations

import asyncio
import contextlib
import typing
from functools import cached_property

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session

from appboot.conf import settings as appboot_settings
from appboot.conf.default import DataBases, EngineConfig
from appboot.exceptions import DatabaseError


class EngineManager:
    def __init__(self, settings: DataBases | None = None):
        self._settings = settings
        self._connections: dict[str, AsyncEngine] = {}
        self.slave_router = self.round_robin()

    def round_robin(self):
        while 1:
            yield from self.all()

    @cached_property
    def settings(self) -> DataBases:
        if self._settings is None:
            self._settings = appboot_settings.DATABASES
        if 'default' not in self._settings:
            raise DatabaseError("You must define a 'default' database.")
        return self._settings

    @property
    def default_engine(self):
        return self['default']

    def create_engine(self, alias: str) -> AsyncEngine:
        config: EngineConfig = self.settings[alias]
        return create_async_engine(
            url=str(config.url),
            future=True,
            **config.dict(exclude={'url'}, exclude_unset=True),
        )

    def __getitem__(self, alias) -> AsyncEngine:
        if alias not in self.settings:
            raise DatabaseError(f"DB '{alias}' doesn't exist.")
        if alias not in self._connections:
            engine = self.create_engine(alias)
            self._connections[alias] = engine
        return self._connections[alias]

    def __setitem__(self, key, value):
        self._connections[key] = value

    def __delitem__(self, key):
        self._connections.pop(key)

    def __iter__(self):
        return iter(self.settings)

    def all(self):
        return [self[alias] for alias in self]

    @property
    def master(self):
        return self.default_engine

    @property
    def slave(self):
        return next(self.slave_router)


engine_manager = EngineManager()


class RoutingSession(Session):
    def get_bind(self, *args, **kwargs):
        if self._flushing:
            return engine_manager.master.sync_engine
        else:
            return engine_manager.slave.sync_engine


class RoutingAsyncSession(AsyncSession):
    sync_session_class = RoutingSession


ScopedSession = async_scoped_session(
    async_sessionmaker(class_=RoutingAsyncSession, expire_on_commit=False),
    scopefunc=asyncio.current_task,
)


class Base(DeclarativeBase):
    pass


@contextlib.asynccontextmanager
async def transaction() -> typing.AsyncIterator[AsyncSession]:
    session = ScopedSession()
    try:
        yield session
        await session.commit()
    except BaseException:
        await session.rollback()
        raise
    finally:
        await ScopedSession.remove()


async def create_tables():
    async with engine_manager.default_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
