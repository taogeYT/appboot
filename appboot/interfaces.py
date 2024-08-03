from __future__ import annotations

from typing import (
    Any,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)

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

    async def get(self, pk: int) -> T:
        ...

    async def flush(self, objects: Optional[Sequence[Any]] = None) -> None:
        ...

    async def bulk_create(self, instances: list[T], flush=False) -> list[T]:
        ...

    async def create(self, **values: dict[str, Any]) -> T:
        ...

    async def update(self, **values: dict[str, Any]) -> int:
        ...

    async def delete(self) -> int:
        ...
