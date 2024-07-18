import asyncio
import contextlib
import typing

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.sql.base import ExecutableOption

from appboot import settings

default_config = settings.DATABASES.default

engine = create_async_engine(
    url=str(default_config.url),
    future=True,
    **default_config.dict(exclude={"url"}, exclude_defaults=True),
)

ScopedSession = async_scoped_session(
    async_sessionmaker(engine), scopefunc=asyncio.current_task
)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

    @declared_attr.directive  # noqa
    @classmethod
    def __deleted_at_option__(cls) -> typing.Optional[ExecutableOption]:
        return None


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
