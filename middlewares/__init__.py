from aiogram import Dispatcher

from .auth import AuthMiddleware
from .db import DatabaseMiddleware


def setup(dp: Dispatcher):
    dp.update.middleware.register(DatabaseMiddleware())
    dp.update.middleware.register(AuthMiddleware())
