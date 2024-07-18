import typing
from datetime import datetime
from typing import Optional, TypeVar

from sqlalchemy import func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, with_loader_criteria
from sqlalchemy.sql.base import ExecutableOption
from typing_extensions import Self

from appboot.db import Base
from appboot.interfaces import BaseRepository
from appboot.repository import Repository
from appboot.utils import camel_to_snake

ModelT = TypeVar("ModelT", bound="Model")


class TableNameMixin:
    @declared_attr.directive  # noqa
    @classmethod
    def __tablename__(cls) -> Optional[str]:
        return camel_to_snake(cls.__name__)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )


class OperatorMixin:
    create_by: Mapped[int] = mapped_column(default=0)
    update_by: Mapped[int] = mapped_column(default=0)


class DeletedAtMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)

    @declared_attr.directive  # noqa
    @classmethod
    def __deleted_at_option__(cls) -> typing.Optional[ExecutableOption]:
        return with_loader_criteria(cls, cls.deleted_at.is_(None))


class Model(TableNameMixin, Base):
    __abstract__ = True
    objects: typing.ClassVar[BaseRepository[Self]] = Repository()
