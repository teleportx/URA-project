from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def find_button_by_callback_data(reply_markup: InlineKeyboardMarkup, callback_data: str) -> InlineKeyboardButton:
    for line in reply_markup.inline_keyboard:
        for button in line:
            if button.callback_data == callback_data:
                return button
