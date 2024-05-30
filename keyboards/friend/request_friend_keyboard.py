from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ActionRequestUserCallback(CallbackData, prefix="aru"):
    uid: int
    requested_uid: int
    result: bool


def get(uid: int, requested_uid: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Отклонить',
        callback_data=ActionRequestUserCallback(uid=uid, requested_uid=requested_uid, result=False).pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Принять',
        callback_data=ActionRequestUserCallback(uid=uid, requested_uid=requested_uid, result=True).pack()
    ))

    return kb.as_markup()
