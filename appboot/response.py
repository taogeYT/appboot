from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")
M = TypeVar("M")


class Page(BaseModel):
    page: int = Field(default=1, ge=1, title="current page")
    size: int = Field(default=10, ge=0, le=100, title="current size")


class PageInfo(Page):
    count: int = Field(default=0, title="total count")


class Response(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class MetaResponse(Response[T], Generic[T, M]):
    meta: Optional[M] = None


class PagePaginationResponse(MetaResponse[T, PageInfo]):
    pass
