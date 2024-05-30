from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get(autoend: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text=f'{["Включить", "Выключить"][autoend]} автозавершение сранья',
        callback_data='chg_aend_srat'
    ))

    return kb.as_markup()
