from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Notify(CallbackData, prefix="not"):
    action: str


def get(only_cancel: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Отменить',
        callback_data=Notify(action='cancel').pack()
    ))

    if not only_cancel:
        kb.add(InlineKeyboardButton(
            text='Подтвердить',
            callback_data=Notify(action='submit').pack()
        ))

    return kb.as_markup()
