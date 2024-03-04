from datetime import timedelta

from aiogram import types, Router
from aiogram.filters import Command, CommandObject

import config
from db.User import User
from filters.user import UserAuthFilter

router = Router()


@router.message(Command("add"), UserAuthFilter(admin=True))
async def add(message: types.Message, command: CommandObject):
    if command.args is None or not command.args.isnumeric():
        await message.reply('Айди должен быть числом')
        return

    await User.create(uid=int(command.args))
    await message.reply('Успешно!')


@router.message(Command("remove"), UserAuthFilter(admin=True))
async def remove(message: types.Message, command: CommandObject):
    if command.args is None or not command.args.isnumeric():
        await message.reply('Айди должен быть числом')
        return

    deleted = await User.filter(uid=int(command.args)).delete()
    if not deleted:
        await message.reply('Пользователь не найден')
        return

    await config.Telegram.bot.ban_chat_member(config.Telegram.group_id, int(command.args), timedelta(seconds=30))

    await message.reply('Успешно!')
