from typing import List

import aiogram
from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.User import User
from db.UserUnion import Channel
from utils import paged_keyboard

channels_on_one_page = 1
channel_members_on_one_page = 1


class ChannelCallbackData(CallbackData, prefix="chn"):
    channel_id: int
    action: str


class ChannelMemberDeleteCallbackData(CallbackData, prefix="chnmd"):
    channel_id: int
    user_id: int
    submit: bool


class ChannelPagedCallbackData(paged_keyboard.PagedCallbackData, prefix="chnp"):
    channel_id: int = -1
    unit: str


async def get_menu(user: User, page: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Создать',
        callback_data=ChannelCallbackData(channel_id=-1, action='create').pack()
    ))

    channels = await user.channels_member.all().offset(channels_on_one_page * page).limit(channels_on_one_page + 1)

    navigation, i = paged_keyboard.draw_page_navigation(channels, page, channels_on_one_page,
                                                        page_callback_data_class=ChannelPagedCallbackData, unit='menu')
    kb.add(*navigation)

    for channel in channels:
        kb.add(InlineKeyboardButton(
            text=channel.name,
            callback_data=ChannelCallbackData(channel_id=channel.channel_id, action='channel').pack()
        ))

    kb.adjust(1 + i, 3)

    return kb.as_markup()


def get_channel(channel_id: int, is_owner: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Назад',
        callback_data=ChannelPagedCallbackData(unit='menu', page=0).pack()
    ))

    if not is_owner:
        kb.add(InlineKeyboardButton(
            text='Покинуть',
            callback_data=ChannelPagedCallbackData(unit='menu', page=0).pack()
        ))

        return kb.as_markup()

    kb.row(InlineKeyboardButton(
        text='Участники',
        callback_data=ChannelPagedCallbackData(channel_id=channel_id, unit='members', page=0).pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Изменить ссылку',
        callback_data=ChannelCallbackData(channel_id=channel_id, action='password').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Пердежи',
        callback_data=ChannelCallbackData(channel_id=channel_id, action='perdish').pack()
    ))

    kb.row(InlineKeyboardButton(
        text='Обновить имя',
        callback_data=ChannelCallbackData(channel_id=channel_id, action='name').pack()
    ))

    kb.row(InlineKeyboardButton(
        text='Удалить канал',
        callback_data=ChannelCallbackData(channel_id=channel_id, action='delete').pack()
    ))

    return kb.as_markup()


def get_channel_delete_submit(channel_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Отменить',
        callback_data=ChannelCallbackData(channel_id=channel_id, action='channel').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Подтвердить',
        callback_data=ChannelCallbackData(channel_id=channel_id, action='delete_submit').pack()
    ))

    return kb.as_markup()


async def get_channel_members(channel: Channel, page: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='К каналу',
        callback_data=ChannelCallbackData(channel_id=channel.channel_id, action='channel').pack()
    ))

    members = await channel.members.all().offset(channel_members_on_one_page * page).limit(channels_on_one_page + 1)

    navigation, i = paged_keyboard.draw_page_navigation(members, page, channels_on_one_page,
                                                        page_callback_data_class=ChannelPagedCallbackData,
                                                        unit='menu', channel_id=channel.channel_id)
    kb.add(*navigation)

    for el in members:
        kb.add(InlineKeyboardButton(
            text=el.name,
            callback_data=ChannelMemberDeleteCallbackData(channel_id=channel.channel_id, user_id=el.uid, submit=False).pack()
        ))

    kb.adjust(1 + i, 3)

    return kb.as_markup()


def get_delete_user_submit(channel_id: int, user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Отменить',
        callback_data=ChannelPagedCallbackData(channel_id=channel_id, unit='members', page=0).pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Подтвердить',
        callback_data=ChannelMemberDeleteCallbackData(channel_id=channel_id, user_id=user_id, submit=True).pack()
    ))

    return kb.as_markup()
