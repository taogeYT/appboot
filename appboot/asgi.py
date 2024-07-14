import importlib

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from appboot import settings
from appboot.db import transaction
from appboot.exceptions import Error


def get_asgi_application():
    return get_fastapi_application()


async def get_session():
    async with transaction() as session:
        yield session


def get_fastapi_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        **settings.FASTAPI_CONFIG.dict(),
        dependencies=[Depends(transaction)],
    )
    app.add_middleware(
        CORSMiddleware,  # type ignore
        allow_origins=settings.ALLOWED_HOSTS,
        allow_methods=settings.ALLOW_METHODS,
        allow_headers=settings.ALLOW_HEADERS,
    )
    fastapi_register_exception(app)
    fastapi_register_routers(app)
    return app


def fastapi_register_exception(app: FastAPI):
    @app.exception_handler(Error)
    async def app_error_handler(request: Request, exc: Error):
        return ORJSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(Exception)
    async def http_exception_handler(request: Request, exc: Exception):
        return ORJSONResponse({"detail": str(exc)}, status_code=500)


def fastapi_register_routers(app: FastAPI):
    mod = importlib.import_module(settings.ROOT_URLCONF)
    for r in mod.routers:
        app.include_router(r)

    @app.get("/ping", summary="ping")
    async def ping():
        return {"data": "pong"}
