from fastapi import Request
from fastapi.responses import JSONResponse


class ExceptionHandler:
    def __init__(self, request: Request, exc: Exception):
        self.request = request
        self.exc = exc

    async def make_response(self):
        status_code = 500
        if isinstance(self.exc, Error):
            status_code = 400
        return JSONResponse({'detail': str(self.exc)}, status_code=status_code)


class Error(Exception):
    pass


class FilterError(Error):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class DoesNotExist(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass
