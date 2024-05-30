from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject

from db.User import User

router = Router()


@router.message(Command("switchdefaultautoend"))
async def switchdefaultautoend(message: types.Message, user: User):
    user.autoend = not user.autoend
    await user.save()

    await message.reply(f'*{["Выключили", "Включили"][user.autoend]}* автозавершение по умолчанию.')


@router.message(Command("setautoendtime"))
async def setautoendtime(message: types.Message, command: CommandObject, user: User):
    args = command.args
    if args is None:
        args = ''

    if not args.isnumeric():
        await message.reply('Пример:\n`/setautoendtime <time in minutes>`')
        return

    if not(3 <= int(args) <= 60):
        await message.reply('Время автозавершения должно быть *не меньше 3 и не больше 60 минут.*')
        return

    user.autoend_time = int(args)
    await user.save()

    await message.reply(f'Теперь ваше время автозавершения сранья: *{args} минут*!')
