from abc import ABC
from typing import Any, Dict, Callable

from aiogram import types

import config
from db.User import User, Ban
from bot_service.middlewares.util import UtilMiddleware


first_join_message_text = '''Добро пожаловать в УРА!

*Команды:*
/guide - Гайд по боту
/credits - О боте'''


class AuthMiddleware(UtilMiddleware, ABC):
    async def __call__(
        self,
        handler: Callable,
        event: types.Update,
        data: Dict[str, Any]
    ) -> Any:
        user = self.get_user(event)

        if await Ban.filter(uid=user.id).exists():
            return

        db_user = await User.filter(uid=user.id).get_or_none()

        if db_user is None:
            db_user = await User.create(uid=user.id, name=user.full_name)
            try:
                await config.bot.send_message(user.id, first_join_message_text)

            except:
                ...

        data['user'] = db_user

        return await handler(event, data)
