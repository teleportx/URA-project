from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject

from db.User import User

router = Router()


@router.message(Command("setnickname"))
async def setnickname(message: types.Message, command: CommandObject, user: User):
    if command.args is None:
        await message.reply('Пример:\n`/setnickname <name>`')
        return

    if len(command.args) > 129:
        await message.reply('Имя должно быть не длиннее 129 символов.')
        return

    if not command.args.replace(' ', '').isalpha():
        await message.reply('Имя не должно содержать специальные символы.')
        return

    user.name = command.args
    await user.save()

    await message.reply(f'Ваш никнейм установлен на *{user.name}*')
