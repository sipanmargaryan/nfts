from fastapi import FastAPI

from .helpers.exception_handlers import register_exception_handlers
from .helpers.middleware import register_middlewares
from .helpers.router_register import register_routers


def create_app() -> FastAPI:
    app = FastAPI(title="Nft app", version="1.0.0")

    register_exception_handlers(app)
    register_middlewares(app)
    register_routers(app)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
