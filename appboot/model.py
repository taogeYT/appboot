from datetime import datetime
from typing import Optional, TypeVar, Type

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

Column = mapped_column
ModelT = TypeVar('ModelT', bound='Model')
SchemaT = TypeVar('SchemaT', bound='BaseSchema')


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
        model: Type[ModelT] = Model

    id: int = Field(default=0)
    created_at: datetime = Field(default=0)
    updated_at: datetime = Field(default=0)
    deleted_at: Optional[datetime] = Field(default=None)
    model_config = ConfigDict(from_attributes=True)
