from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.User import User


class ApiCallback(CallbackData, prefix="api"):
    action: str
    token: Optional[str] = None


async def get(user: User) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='+ Новый токен',
        callback_data=ApiCallback(action='new').pack()
    ))

    async for token in user.tokens_owned.filter(valid=True):
        kb.row(InlineKeyboardButton(
            text=token.name,
            callback_data=ApiCallback(action='revoke', token=str(token.pk)).pack()
        ))

    return kb.as_markup()


def get_revoke_submit(token_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text=f'Отменить',
        callback_data=ApiCallback(action='menu').pack()
    ))

    kb.add(InlineKeyboardButton(
        text=f'Подтвердить',
        callback_data=ApiCallback(action='revoke_submit', token=token_id).pack()
    ))

    return kb.as_markup()
