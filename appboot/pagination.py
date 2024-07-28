from __future__ import annotations

import typing

from pydantic import Field

from appboot.schema import Schema

if typing.TYPE_CHECKING:
    from appboot.repository import Repository


T = typing.TypeVar('T')


class BasePage(Schema):
    page: int = Field(1, ge=1, le=10000, title='current page num')
    page_size: int = Field(10, ge=0, le=100, title='current page size')


class PaginationResult(BasePage, typing.Generic[T]):
    count: int
    results: list[T]


class PagePagination(BasePage):
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    async def paginate(self, repository: Repository):
        count = await repository.count()
        results = await repository.limit(self.page_size).offset(self.offset).all()
        return PaginationResult(
            count=count, results=results, page=self.page, page_size=self.page_size
        )
