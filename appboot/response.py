from typing import Generic, Optional, TypeVar

from fastapi import HTTPException

from appboot.exceptions import Error
from appboot.schema import Schema

T = TypeVar('T')


class APIResponse(Schema, Generic[T]):
    code: int = 200
    message: str = 'success'
    data: Optional[T] = None

    @classmethod
    def from_exception(cls, e: Exception) -> 'APIResponse':
        if isinstance(e, HTTPException):
            return cls(code=e.status_code, message=e.detail)
        if isinstance(e, Error):
            return cls(code=e.code, message=str(e))
        return cls(code=500, message=str(e))
