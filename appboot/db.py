from __future__ import annotations

import asyncio
import contextlib
import typing

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from appboot.conf import settings

default_config = settings.DATABASES.default

engine = create_async_engine(
    url=str(default_config.url),
    future=True,
    **default_config.dict(exclude={'url'}, exclude_unset=True),
)

ScopedSession = async_scoped_session(
    async_sessionmaker(engine, expire_on_commit=False), scopefunc=asyncio.current_task
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
