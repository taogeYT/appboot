from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from appboot.schema import Schema

T = TypeVar('T')


@runtime_checkable
class BaseRepository(Protocol[T]):
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

    def group_by(self, __first, *clauses):
        ...

    def having(self, *having):
        ...

    def join(
        self,
        target: Any,
        onclause: Optional[Any] = None,
        *,
        isouter: bool = False,
        full: bool = False,
    ):
        ...

    def with_for_update(
        self,
        *,
        nowait: bool = False,
        read: bool = False,
        of: Optional[Any] = None,
        skip_locked: bool = False,
        key_share: bool = False,
    ):
        ...

    def with_entities(self, *entities: Any, **__kw: Any):
        ...

    @property
    def statement(self):
        ...

    def clone(self):
        ...

    async def count(self) -> int:
        ...

    async def all(self) -> Sequence[T]:
        ...

    async def first(self) -> Optional[T]:
        ...

    async def get(self, pk: int) -> Optional[T]:
        ...

    async def bulk_create(self, objs: list[Schema], flush=False) -> list[T]:
        ...

    async def create(self, obj: Schema, flush=False) -> T:
        ...

    async def update(self, values: dict[str, Any]) -> int:
        ...

    async def update_one(self, pk: int, obj: Schema, flush=False) -> T:
        ...

    async def delete_one(self, pk: int, flush=False) -> T:
        ...
