import asyncio
import json
import logging

from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import config

router = Router()
going = []


@router.message(Command("start"))
async def start(message: types.Message):
    if message.chat.id not in config.Telegram.users:
        await message.reply('Извините, вы не можете уведомлять всех о том, что вы идете срать.\n\n'
                            'Если вы все же хотите это делать, напишите администратору бота с просьбой об этом.\n'
                            f'*Ваш id:* `{message.chat.id}`',
                            parse_mode='markdown')

    else:
        kb = ReplyKeyboardBuilder()

        kb.button(text='Я иду ЛЮТЕЙШЕ ДРИСТАТЬ ПОНОСОМ')
        kb.button(text='Я иду срать')
        kb.adjust(1)
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


@router.message()
async def notify(message: types.Message):
    await message.delete()

    if message.text == 'Я иду срать':
        text = '⚠️ *ВНИМАНИЕ* ⚠️\n' \
               '`%s` *прямо сейчас* пошел _срать_'

    elif message.text == 'Я закончил срать':
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '`%s` закончил _срать_'

    elif message.text == 'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ ПОНОСОМ':
        text = '⚠️️️️⚠️⚠️ ВНИМАНИЕ ⚠️⚠️⚠️\n\n' \
               '⚠️НАДВИГАЕТСЯ *ГОВНОПОКАЛИПСИС*⚠️\n' \
               '`%s` *прямо сейчас* пошел _адски дристать_ лютейшей струей *поноса*'


    else:
        return

    for user in config.Telegram.users:
        try:
            await config.Telegram.bot.send_message(user, text % message.chat.full_name,
                                                   parse_mode='markdown')

        except Exception as e:
            logging.warning(f'Cannnot send notify to {message.chat.id} cause: {e}')
