import asyncio
from datetime import timedelta

from aiogram import Router
from aiogram import types
from aiogram.filters import Command

import config
from filters.user import UserAuthFilter

router = Router()


@router.message(Command("link"), UserAuthFilter())
async def link(message: types.Message):
    invite_link = await config.Telegram.bot.create_chat_invite_link(
        config.Telegram.group_id,
        message.from_user.full_name,
        timedelta(seconds=10),
        1,
    )

    replied = await message.reply(invite_link.invite_link)

    await asyncio.sleep(10)
    await message.delete()
    await replied.delete()
