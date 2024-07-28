from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = 'success'
    data: Optional[T] = None
