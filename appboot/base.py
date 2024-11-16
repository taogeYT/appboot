from __future__ import annotations

import typing
from typing import Any

from pydantic import BaseModel, ConfigDict
from typing_extensions import Self

from appboot._compat import PYDANTIC_V2


class Schema(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    else:

        class Config:
            orm_mode = True
            allow_population_by_field_name = True

    @classmethod
    def from_orm_many(cls, objs: typing.Sequence[Any]) -> list[Self]:
        return [cls.from_orm(obj) for obj in objs]

    @classmethod
    def parse_obj(cls, obj: Any) -> Self:  # noqa: D102
        if PYDANTIC_V2:
            return cls.model_validate(obj)
        else:
            return super().parse_obj(obj)

    @classmethod
    def from_orm(cls, obj: Any) -> Self:
        if PYDANTIC_V2:
            return cls.model_validate(obj)
        else:
            return super().from_orm(obj)

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> dict[str, typing.Any]:
        if PYDANTIC_V2:
            return self.model_dump(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
        else:
            return super().dict(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
