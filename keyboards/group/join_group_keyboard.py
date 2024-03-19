from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class JoinGroupCallback(CallbackData, prefix="grpj"):
    uid: int
    group_id: int
    result: bool


def get(uid: int, group_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Отклонить',
        callback_data=JoinGroupCallback(uid=uid, group_id=group_id, result=False).pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Принять',
        callback_data=JoinGroupCallback(uid=uid, group_id=group_id, result=True).pack()
    ))

    return kb.as_markup()
