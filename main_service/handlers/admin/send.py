from aiogram import Router
from aiogram import types
from aiogram.filters import CommandObject

import config
from main_service.filters import CommandMention
from main_service.filters import UserAuthFilter

router = Router()


@router.message(CommandMention("send"), UserAuthFilter(admin=True))
async def send(message: types.Message, command: CommandObject):
    args = command.args
    if args is None:
        args = ''
    args = args.split()

    if len(args) < 2:
        await message.reply('Пример:\n<code>/send &#60;user_id&#62; &#60;message&#62;</code>')
        return

    if not args[0].isnumeric():
        await message.reply('Айди должно быть числом.')
        return

    try:
        await config.bot.send_message(args[0], '❗️ <b>Сообщение от админов:</b>\n' + ' '.join(args[1:]))
        await message.reply('Сообщение отправлено!')

    except:
        await message.reply('Не удалось отправить сообщение.')
