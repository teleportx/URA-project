from fastapi import FastAPI

from .auth import AuthMiddleware


def setup(app: FastAPI, raise_unauthorized: bool = False):
    app.add_middleware(AuthMiddleware, raise_unauthorized=raise_unauthorized)
