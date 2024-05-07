from aiogram import Router
from aiogram import types
from aiogram.filters import Command

from db.User import User

router = Router()


@router.message(Command("switchdefaultautoend"))
async def switchdefaultautoend(message: types.Message, user: User):
    user.autoend = not user.autoend
    await user.save()

    await message.reply(f'*{["Выключили", "Включили"][user.autoend]}* автозавершение по умолчанию.')
