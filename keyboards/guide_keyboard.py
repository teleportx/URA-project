from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class GuideCallbackData(CallbackData, prefix="gud"):
    unit: str


def get() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Группы',
        callback_data=GuideCallbackData(unit='groups').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Каналы',
        callback_data=GuideCallbackData(unit='channels').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Друзья',
        callback_data=GuideCallbackData(unit='friends').pack()
    ))

    kb.row(InlineKeyboardButton(
        text='Кастомизация',
        callback_data=GuideCallbackData(unit='customization').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Полезное',
        callback_data=GuideCallbackData(unit='utils').pack()
    ))

    return kb.as_markup()


def get_return() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Назад',
        callback_data=GuideCallbackData(unit='main').pack()
    ))

    return kb.as_markup()
