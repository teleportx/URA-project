from aiogram import Router
from aiogram import types
from aiogram.filters import Command

from filters.command_args import CommandArgsStartswith
from keyboards import srat_var_keyboard

router = Router()


@router.message(Command("start"), CommandArgsStartswith())
async def start(message: types.Message):
    await message.reply('Выберете действие.', reply_markup=srat_var_keyboard.get())
