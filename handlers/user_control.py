from aiogram import types, Router
from aiogram.filters import Command, CommandObject

from db.User import User
from filters.user import UserAuthFilter

router = Router()


@router.message(Command("add"), UserAuthFilter(admin=True))
async def add(message: types.Message, command: CommandObject):
    if command.args is None or not command.args.isnumeric():
        await message.reply('Айди должен быть числом')
        return

    User.create(uid=int(command.args))
    await message.reply('Успешно!')


@router.message(Command("remove"), UserAuthFilter(admin=True))
async def remove(message: types.Message, command: CommandObject):
    if command.args is None or not command.args.isnumeric():
        await message.reply('Айди должен быть числом')
        return

    deleted = User.delete_by_id(int(command.args))
    if not deleted:
        await message.reply('Пользователь не найден')
        return

    await message.reply('Успешно!')
