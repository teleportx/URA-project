from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware
from .auth import AuthMiddleware
from .db import DatabaseMiddleware
from .degrade import DegradationMiddleware


def setup(dp: Dispatcher):
    dp.update.middleware.register(ThrottlingMiddleware())
    dp.update.middleware.register(DatabaseMiddleware())
    dp.update.middleware.register(AuthMiddleware())
    dp.update.middleware.register(DegradationMiddleware())
