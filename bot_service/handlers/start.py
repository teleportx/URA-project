from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, MagicData

from keyboards import srat_var_keyboard

router = Router()


@router.message(Command("start"), MagicData(~F.command.args))
async def start(message: types.Message):
    await message.reply('Выберете действие.', reply_markup=srat_var_keyboard.get())
