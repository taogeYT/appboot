from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from appboot.schema import ModelSchema

T = TypeVar('T')


@runtime_checkable
class BaseRepository(Protocol[T]):
    def disable_option(self):
        ...

    def filter(self, *condition):
        ...

    def filter_by(self, **kwargs):
        ...

    def limit(self, num: int):
        ...

    def offset(self, num: int):
        ...

    def slice(self, start: int, end: int):
        ...

    def options(self, *args):
        ...

    def order_by(self, *args):
        ...

    def get_query(self):
        ...

    async def all(self) -> Sequence[T]:
        ...

    async def first(self) -> Optional[T]:
        ...

    async def get(self, pk: int) -> Optional[T]:
        ...

    async def bulk_create(self, objs: list[ModelSchema], flush=False) -> list[T]:
        ...

    async def create(self, obj: ModelSchema, flush=False) -> T:
        ...

    async def update(self, pk: int, obj: ModelSchema, flush=False) -> T:
        ...

    async def delete(self, pk: int, flush=False) -> T:
        ...
