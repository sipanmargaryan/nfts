from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change this in production!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
