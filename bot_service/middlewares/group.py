from abc import ABC
from typing import Any, Dict, Callable

from aiogram import types

from db.UserUnion import Group
from keyboards.group import groups_keyboard
from bot_service.middlewares.util import UtilMiddleware


class GroupMiddleware(UtilMiddleware, ABC):
    async def __call__(
            self,
            handler: Callable,
            event: types.Update,
            data: Dict[str, Any]
    ) -> Any:
        try:
            callback = groups_keyboard.GroupCallback.unpack(event.data)
            if callback.group == -1:
                raise ModuleNotFoundError

            group = await Group.filter(pk=callback.group).get_or_none()
            if group is None:
                await event.answer('Группы не существует.', show_alert=True)
                await event.message.edit_text('Выберете группу.',
                                              reply_markup=await groups_keyboard.get_all(data['user']))
                return

            data['group'] = group

        except (ModuleNotFoundError, TypeError):
            ...

        return await handler(event, data)
