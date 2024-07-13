import asyncio
import contextlib

from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from appboot import settings

default_config = settings.DATABASES.default

engine = create_async_engine(
    url=default_config.url,
    pool_size=default_config.pool_size,
    max_overflow=default_config.max_overflow,
    pool_recycle=default_config.pool_recycle,
    future=True,
    echo=default_config.echo,
)

ScopedSession = async_scoped_session(
    async_sessionmaker(engine), scopefunc=asyncio.current_task
)


@contextlib.asynccontextmanager
async def transaction() -> AsyncSession:
    session = ScopedSession()
    try:
        yield session
        await session.commit()
    except BaseException:
        await session.rollback()
        raise
    finally:
        await ScopedSession.remove()
