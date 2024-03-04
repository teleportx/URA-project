import logging

from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject

import config
from db.User import User
from filters.user import UserAuthFilter

router = Router()


@router.message(Command("notify"), UserAuthFilter(admin=True))
async def notify(message: types.Message, command: CommandObject):
    async for user in User.all():
        try:
            await config.Telegram.bot.send_message(user.uid, '❗️*Уведомление*\n' + command.args,
                                                   parse_mode='markdown')

        except Exception as e:
            logging.warning(f'Cannnot send notify to {message.chat.id} cause: {e}')
