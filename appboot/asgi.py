import importlib

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from appboot.conf import settings
from appboot.db import transaction
from appboot.exceptions import Error


class ExceptionHandler:
    exceptions = [Error, Exception]

    def __init__(self, request: Request, exc: Exception):
        self.request = request
        self.exc = exc

    async def make_response(self):
        status_code = 500
        if isinstance(self.exc, Error):
            status_code = self.exc.code
        return JSONResponse({'detail': str(self.exc)}, status_code=status_code)

    @classmethod
    async def handle_exception(cls, request: Request, exc: Exception):
        return await cls(request, exc).make_response()


def get_asgi_application():
    return get_fastapi_application()


async def get_session():
    async with transaction() as session:
        yield session


def get_fastapi_application():
    kw = dict(title=settings.PROJECT_NAME)
    kw.update(settings.FASTAPI)
    kw.update(dependencies=[Depends(get_session)])
    app = FastAPI(**kw)
    app.add_middleware(
        CORSMiddleware,  # type: ignore[unused-ignore]
        allow_origins=settings.ALLOWED_HOSTS,
        allow_methods=settings.ALLOW_METHODS,
        allow_headers=settings.ALLOW_HEADERS,
    )
    fastapi_register_routers(app)
    return app


def fastapi_register_exception(app: FastAPI, handler=ExceptionHandler):
    for exc_cls in handler.exceptions:
        app.exception_handler(exc_cls)(handler.handle_exception)


def fastapi_register_routers(app: FastAPI):
    mod = importlib.import_module(settings.ROOT_URLCONF)
    app.include_router(mod.root_router)
