from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject

import config
from db.User import User

router = Router()


@router.message(Command("switchdefaultautoend"))
async def switchdefaultautoend(message: types.Message, user: User):
    user.autoend = not user.autoend
    await user.save()

    await message.reply(f'<b>{["Выключили", "Включили"][user.autoend]}</b> автозавершение по умолчанию.')


@router.message(Command("setautoendtime"))
async def setautoendtime(message: types.Message, command: CommandObject, user: User):
    args = command.args
    if args is None:
        args = ''

    if not args.isnumeric():
        await message.reply('Пример:\n<code>/setautoendtime &#60;time in minutes&#62;</code>')
        return

    if not(3 <= int(args) <= config.Constants.srat_delete_time):
        await message.reply(f'Время автозавершения должно быть <b>не меньше 3 и не больше {config.Constants.srat_delete_time} минут.</b>')
        return

    user.autoend_time = int(args)
    await user.save()

    await message.reply(f'Теперь ваше время автозавершения сранья: <b>{args} минут</b>!')
