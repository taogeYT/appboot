import typing

from pydantic import Field

from appboot.schema import Schema

if typing.TYPE_CHECKING:
    from appboot.repository import Repository


T = typing.TypeVar('T')


class BasePagination(Schema):
    page: int = Field(1, gt=0, le=10000)
    page_size: int = Field(10, ge=0, le=100)


class PaginationSchema(BasePagination, typing.Generic[T]):
    count: int
    results: list[T]


class Page(BasePagination):
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    async def paginate(self, repository: Repository):
        total = await repository.count()
        results = await repository.limit(self.page_size).offset(self.offset).get_all()
        return PaginationSchema(
            total=total, results=results, page=self.page, page_size=self.page_size
        )
