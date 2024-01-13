from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import config

router = Router()


@router.message(Command("start"))
async def start(message: types.Message, command: CommandObject):
    if message.chat.id not in config.Telegram.users:
        await message.reply('Извините, вы не можете уведомлять всех о том, что вы идете срать.\n\n'
                            'Если вы все же хотите это делать, напишите администратору бота с просьбой об этом.\n'
                            f'**Ваш id:** `{message.chat.id}`',
                            parse_mode='markdown')

    else:
        kb = ReplyKeyboardBuilder()
        kb.button(text='Я иду срать')
        kb.button(text='Я закончил срать')

        await message.reply('Выберете действие.', reply_markup=kb.as_markup())
