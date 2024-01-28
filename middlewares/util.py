from aiogram import BaseMiddleware
from aiogram.types import Update


class UtilMiddleware(BaseMiddleware):
    def get_user(self, event: Update):
        if event.message:
            return event.message.from_user

        elif event.callback_query:
            return event.callback_query.from_user
