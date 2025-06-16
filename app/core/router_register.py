from fastapi import FastAPI

from ..routers.auth import routes as auth
from ..routers.common import routes as common


def register_routers(app: FastAPI):
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(common.router, prefix="/api/v1")
