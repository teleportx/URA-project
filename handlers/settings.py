from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.user import UserAuthFilter

router = Router()

class Privatnost(CallbackData, prefix="pr"):
    ...


@router.message(Command("settings"), UserAuthFilter())
async def settings(message: types.Message):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Сообщать всем, что вы идете срать ✅',
        callback_data=Privatnost().pack())
    )

    builder.row(types.InlineKeyboardButton(
        text='Сообщать всем, что вы идете дристать ✅',
        callback_data=Privatnost().pack())
    )

    builder.row(types.InlineKeyboardButton(
        text='Сообщать всем, что вы закончили срать ✅',
        callback_data=Privatnost().pack())
    )

    builder.row(types.InlineKeyboardButton(
        text='Сообщать всем, что вы просто пернули ✅',
        callback_data=Privatnost().pack())
    )

    await message.reply('Выберете действие.', reply_markup=builder.as_markup())


@router.callback_query(Privatnost.filter(), UserAuthFilter())
async def privatnost(callback: types.CallbackQuery):
    await callback.answer('Хрен тебе, а не приватность.\nНе нравится - не пользуйся.', show_alert=True)
