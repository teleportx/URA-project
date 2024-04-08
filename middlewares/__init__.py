from aiogram import Dispatcher

from .auth import AuthMiddleware
from .db import DatabaseMiddleware
from .degrade import DegradationMiddleware


def setup(dp: Dispatcher):
    dp.update.middleware.register(DatabaseMiddleware())
    dp.update.middleware.register(AuthMiddleware())
    dp.update.middleware.register(DegradationMiddleware())
