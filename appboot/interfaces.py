from typing import Optional, Protocol, Sequence, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T")


@runtime_checkable
class BaseRepository(Protocol[T]):
    def disable_option(self):
        ...

    def get_option(self):
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

    def get_query(self):
        ...

    async def all(self) -> Sequence[T]:
        ...

    async def first(self) -> Optional[T]:
        ...

    async def get(self, pk: int) -> Optional[T]:
        ...

    async def mget(self, pks: list[int]) -> dict[int, T]:
        ...

    async def bulk_create(self, objs: list[BaseModel], flush=False) -> list[T]:
        ...

    async def create(self, obj: BaseModel, flush=False) -> T:
        ...

    async def update(self, pk: int, obj: BaseModel, flush=False) -> T:
        ...

    async def delete(self, pk: int, flush=False) -> T:
        ...
