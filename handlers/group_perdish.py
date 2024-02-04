from aiogram import types, Router, F
from aiogram.enums import ContentType
from aiogram.types import ChatPermissions

import config

router = Router()


@router.message(F.chat.id == config.Telegram.group_id, F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def join_group(message: types.Message):
    permissions = ChatPermissions(can_send_messages=False)
    await config.Telegram.bot.restrict_chat_member(config.Telegram.group_id, message.from_user.id, permissions)
