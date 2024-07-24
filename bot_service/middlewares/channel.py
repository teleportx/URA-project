from abc import ABC
from typing import Any, Dict, Callable

from aiogram import types

from db.UserUnion import Channel
from keyboards.channel import channels_keyboard
from bot_service.middlewares.util import UtilMiddleware


class ChannelMiddleware(UtilMiddleware, ABC):
    def __init__(self, channel_menu_text):
        self.channel_menu_text = channel_menu_text

    async def __call__(
            self,
            handler: Callable,
            event: types.Update,
            data: Dict[str, Any]
    ) -> Any:
        try:
            callback = channels_keyboard.ChannelCallback.unpack(event.data)
            if callback.channel_id == -1:
                raise ModuleNotFoundError

            channel = await Channel.filter(pk=callback.channel_id).get_or_none()
            if channel is None:
                await event.answer('Канала не существует.', show_alert=True)
                await event.message.edit_text(self.channel_menu_text,
                                              reply_markup=await channels_keyboard.get_menu(data['user'], 0))
                return

            data['channel'] = channel

        except (ModuleNotFoundError, TypeError):
            ...

        return await handler(event, data)
