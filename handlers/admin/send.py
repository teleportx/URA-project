from aiogram import Router
from aiogram import types
from aiogram.filters import CommandObject

import config
from filters.command_mention import CommandMention
from filters.user import UserAuthFilter

router = Router()


@router.message(CommandMention("send"), UserAuthFilter(admin=True))
async def send(message: types.Message, command: CommandObject):
    args = command.args
    if args is None:
        args = ''
    args = args.split()

    if len(args) < 2:
        await message.reply('Пример:\n`/send <user_id> <message>`')
        return

    if not args[0].isnumeric():
        await message.reply('Айди должно быть числом.')
        return

    try:
        await config.bot.send_message(args[0], '❗️ *Сообщение от админов:*\n' + ' '.join(args[1:]))
        await message.reply('Сообщение отправлено!')

    except:
        await message.reply('Не удалось отправить сообщение.')
