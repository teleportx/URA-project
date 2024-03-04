from abc import ABC
from typing import Any, Dict, Callable

from aiogram import types

from db.User import User, Ban
from middlewares.util import UtilMiddleware


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

        first_joined = False
        db_user = await User.filter(uid=user.id).get_or_none()

        if db_user is None:
            first_joined = True
            db_user = await User.create(uid=user.id, name=user.full_name)

        data['user'] = db_user
        data['first_joined'] = first_joined

        return await handler(event, data)
