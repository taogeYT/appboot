import sys
import typing
from datetime import datetime
from typing import Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from appboot.interfaces import BaseRepository

Column = mapped_column
ModelT = TypeVar("ModelT", bound="Model")
SchemaT = TypeVar("SchemaT", bound="BaseModelSchema")
if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = typing.Annotated[ModelT, "Self"]


class Model(DeclarativeBase):
    # repository_class: typing.ClassVar[typing.Optional[type[BaseRepository]]]
    objects: typing.ClassVar[BaseRepository[Self]]

    id: Mapped[int] = Column(primary_key=True)
    created_at: Mapped[datetime] = Column(default=func.now())
    updated_at: Mapped[datetime] = Column(default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = Column(default=None)

    def __init_subclass__(cls, **kwargs: dict[str, typing.Any]):
        from appboot.repository import Repository

        super().__init_subclass__(**kwargs)
        cls.objects = Repository()

    def delete(self) -> None:
        if self.deleted_at is None:
            self.deleted_at: datetime = datetime.now()


class OperatorMixin:
    create_by: Mapped[int] = Column(default=0)
    update_by: Mapped[int] = Column(default=0)


class BaseModelSchema(BaseModel):
    id: int = Field(default=0)
    _instance: Optional[ModelT] = None  # type: ignore
    model_config = ConfigDict(from_attributes=True)

    @property
    def instance(self):
        return self._instance

    @classmethod
    def from_sqlalchemy_model(cls: type[SchemaT], instance: ModelT) -> SchemaT:
        raise NotImplementedError
