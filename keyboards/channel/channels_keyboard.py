import aiogram
from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.User import User
from db.UserUnion import Channel

channels_on_one_page = 9


class ChannelCallback(CallbackData, prefix="chn"):
    channel_id: int
    action: str


class ChannelPagedCallback(CallbackData, prefix="chn"):
    unit: str
    page: int


async def get_menu(user: User, page: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Создать',
        callback_data=ChannelCallback(channel_id=-1, action='create').pack()
    ))

    i = 0
    if page != 0:
        i += 1
        kb.add(InlineKeyboardButton(
            text='◀',
            callback_data=ChannelPagedCallback(unit='menu', page=page - 1).pack()
        ))

    channels = await user.channels_member.all().offset(channels_on_one_page * page).limit(channels_on_one_page + 1)

    if len(channels) == channels_on_one_page + 1:
        i += 1
        kb.add(InlineKeyboardButton(
            text='▶',
            callback_data=ChannelPagedCallback(unit='menu', page=page + 1).pack()
        ))
        channels.pop()

    for channel in channels:
        kb.add(InlineKeyboardButton(
            text=channel.name,
            callback_data=ChannelCallback(channel_id=channel.channel_id, action='channel').pack()
        ))

    kb.adjust(1 + i, 3)

    return kb.as_markup()


def get_channel(channel_id: int, is_owner: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Назад',
        callback_data=ChannelPagedCallback(unit='menu', page=0).pack()
    ))

    if not is_owner:
        kb.add(InlineKeyboardButton(
            text='Покинуть',
            callback_data=ChannelPagedCallback(unit='menu', page=0).pack()
        ))

        return kb.as_markup()

    kb.row(InlineKeyboardButton(
        text='Участники',
        callback_data=ChannelCallback(channel_id=channel_id, action='members').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Изменить ссылку',
        callback_data=ChannelCallback(channel_id=channel_id, action='password').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Пердежи',
        callback_data=ChannelCallback(channel_id=channel_id, action='perdish').pack()
    ))

    kb.row(InlineKeyboardButton(
        text='Удалить канал',
        callback_data=ChannelCallback(channel_id=channel_id, action='delete').pack()
    ))

    return kb.as_markup()
