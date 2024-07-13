from datetime import datetime
from typing import Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

Column = mapped_column
ModelT = TypeVar("ModelT", bound="Model")
SchemaT = TypeVar("SchemaT", bound="BaseSchema")


class Model(DeclarativeBase):
    id: Mapped[int] = Column(primary_key=True)
    created_at: Mapped[datetime] = Column(default=func.now())
    updated_at: Mapped[datetime] = Column(default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = Column(default=None)


class OperatorMixin:
    create_by: Mapped[int] = Column(default=0)
    update_by: Mapped[int] = Column(default=0)


class BaseSchema(BaseModel):
    class Meta:
        model = Model

    id: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)
    model_config = ConfigDict(from_attributes=True)
