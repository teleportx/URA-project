import asyncio
import json

from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import config

router = Router()


@router.message(Command("start"))
async def start(message: types.Message):
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


@router.message(Command("add"))
async def add(message: types.Message, command: CommandObject):
    if message.chat.id not in config.Telegram.admins:
        return

    if not command.args.isnumeric():
        await message.reply('Айди должен быть числом')
        return

    config.Telegram.users.add(int(command.args))

    with open(config.data_file, 'w') as fp:
        fp.truncate()
        json.dump(list(config.Telegram.users), fp)

    await message.reply('Успешно!')

    await asyncio.sleep(5)


@router.message(Command("remove"))
async def add(message: types.Message, command: CommandObject):
    if message.chat.id not in config.Telegram.admins:
        return

    if not command.args.isnumeric():
        await message.reply('Айди должен быть числом')
        return

    if int(command.args) not in config.Telegram.users:
        await message.reply('Пользователь не найден')
        return

    config.Telegram.users.remove(int(command.args))

    with open(config.data_file, 'w') as fp:
        fp.truncate()
        json.dump(list(config.Telegram.users), fp)

    await message.reply('Успешно!')

    await asyncio.sleep(5)
