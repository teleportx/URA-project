from aiogram import types, Router, F
from aiogram.enums import ContentType
from aiogram.types import ChatPermissions

import config
from db.User import User
from filters.user import UserAuthFilter

router = Router()


@router.message(UserAuthFilter(), F.chat.id == config.Telegram.group_id, F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def join_group(message: types.Message, user: User):
    permissions = ChatPermissions(can_send_messages=user.sret is not None)
    await config.Telegram.bot.restrict_chat_member(config.Telegram.group_id, message.from_user.id, permissions)
