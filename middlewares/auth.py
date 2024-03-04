from abc import ABC
from typing import Any, Dict, Callable

from aiogram import types

from db.User import User
from middlewares.util import UtilMiddleware


class AuthMiddleware(UtilMiddleware, ABC):
    async def __call__(
        self,
        handler: Callable,
        event: types.Update,
        data: Dict[str, Any]
    ) -> Any:
        user = self.get_user(event)

        data['user'] = await self.get_bot_user(user)
        return await handler(event, data)

    async def get_bot_user(self, user: types.User) -> User:
        db_user = await User.filter(uid=user.id).first()

        if db_user is not None and db_user.name != user.full_name:
            db_user.name = user.full_name
            await db_user.save()

        return db_user
