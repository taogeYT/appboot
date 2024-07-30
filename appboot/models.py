from __future__ import annotations

import typing
from datetime import datetime
from typing import Optional, TypeVar

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from typing_extensions import Self

from appboot import timezone
from appboot.conf import settings
from appboot.db import Base
from appboot.interfaces import BaseRepository
from appboot.repository import Repository
from appboot.utils import camel_to_snake

ModelT = TypeVar('ModelT', bound='Model')


class TableNameMixin:
    @declared_attr.directive  # noqa
    @classmethod
    def __tablename__(cls) -> str:
        return f'{settings.DEFAULT_TABLE_NAME_PREFIX}{camel_to_snake(cls.__name__)}'


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class OperatorMixin:
    create_by: Mapped[int] = mapped_column(default=0)
    update_by: Mapped[int] = mapped_column(default=0)


class DeletedAtMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # @declared_attr.directive  # noqa
    @classmethod
    def __delete_condition__(cls):
        return cls.deleted_at.is_(None)

    @classmethod
    def __delete_value__(cls) -> dict[str, typing.Any]:
        return {'deleted_at': timezone.now()}


class Model(TableNameMixin, Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    objects: typing.ClassVar[BaseRepository[Self]] = Repository()

    def update(self, **values: dict[str, typing.Any]):
        for name, value in values.items():
            if hasattr(self, name) and getattr(self, name) != value:
                setattr(self, name, value)
