from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.User import User


class FriendUserType(Enum):
    friend = 'f'
    friend_submit = 'fs'
    request = 'r'
    request_submit = 'rs'


class FriendUserCallback(CallbackData, prefix='fru'):
    user_id: int
    type: FriendUserType


class FriendMenuCallback(CallbackData, prefix='frm'):
    unit: str


async def get(user: User) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Ваши заявки',
        callback_data=FriendMenuCallback(unit='req').pack()
    ))

    kb.add(InlineKeyboardButton(
        text=f'{["За", "Раз"][user.mute_friend_requests]}мутить',
        callback_data=FriendMenuCallback(unit='chgmut').pack()
    ))

    async for friend in user.friends:
        kb.row(InlineKeyboardButton(
            text=friend.name,
            callback_data=FriendUserCallback(user_id=friend.uid, type=FriendUserType.friend).pack()
        ))

    kb.adjust(2, 3)
    return kb.as_markup()


async def get_requests(user: User) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Назад',
        callback_data=FriendMenuCallback(unit='main').pack()
    ))

    async for friend_requested in user.friends_requested:
        user_requested = await friend_requested.requested_user
        kb.row(InlineKeyboardButton(
            text=user_requested.name,
            callback_data=FriendUserCallback(user_id=user_requested.uid, type=FriendUserType.request).pack()
        ))

    kb.adjust(1, 3)
    return kb.as_markup()


def get_submit_delete(user_id: int, return_to: str, act_type: FriendUserType) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Отмена',
        callback_data=FriendMenuCallback(unit=return_to).pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Удалить',
        callback_data=FriendUserCallback(user_id=user_id, type=act_type).pack()
    ))

    return kb.as_markup()
