from __future__ import annotations

import typing
from datetime import datetime
from typing import Optional, TypeVar

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.sql.selectable import ForUpdateParameter
from typing_extensions import Self

from appboot import timezone
from appboot.conf import settings
from appboot.db import Base, ScopedSession
from appboot.repository import QuerySet, QuerySetProperty, SoftDeleteQuerySet
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
    query_set_class = SoftDeleteQuerySet
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    async def delete(self):
        self.deleted_at = timezone.now()
        return self


class Model(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    objects: typing.ClassVar[QuerySet[Self]] = QuerySetProperty(ScopedSession)  # type: ignore

    @classmethod
    def construct(cls, **kwargs: dict[str, typing.Any]) -> Self:
        return _parse_data_to_model(cls, kwargs)

    async def update(self, **values: dict[str, typing.Any]):
        for name, value in values.items():
            if hasattr(self, name) and getattr(self, name) != value:
                setattr(self, name, value)

    async def refresh(
        self,
        attribute_names: Optional[typing.Iterable[str]] = None,
        with_for_update: ForUpdateParameter = None,
    ):
        await ScopedSession().refresh(self, attribute_names, with_for_update)
        return self

    async def save(self):
        session = ScopedSession()
        session.add(self)
        await session.flush()


def _parse_data_to_model(model: type[Base], data: dict[str, typing.Any]):
    _data = {}
    for key, column in model.__mapper__.columns.items():
        if key not in data or column.primary_key:
            continue
        _data[key] = data[key]
    for key, rel in model.__mapper__.relationships.items():
        if key not in data:
            continue
        sub_model = rel.mapper.class_
        if rel.uselist:
            rel_result = [
                _parse_data_to_model(sub_model, sub_data) for sub_data in data[key]
            ]
        else:
            rel_result = _parse_data_to_model(sub_model, data[key])
        _data[key] = rel_result
    return model(**_data)
