from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Написать',
        url=f'tg://user?id={user_id}'
    ))

    kb.row(InlineKeyboardButton(
        text='Забанить',
        switch_inline_query_current_chat=f'/ban {user_id} '
    ))

    return kb.as_markup()
