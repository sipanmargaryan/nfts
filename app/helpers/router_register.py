from fastapi import FastAPI

from ..routers.auth import routes as auth
from ..routers.common import routes as common
from ..routers.companies import routes as compannies
from ..routers.users import routes as users


def register_routers(app: FastAPI):
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(common.router, prefix="/api/v1")
    app.include_router(compannies.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
