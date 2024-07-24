from typing import List, Type, Tuple

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


class PagedCallbackData(CallbackData, prefix=''):
    page: int


def draw_page_navigation(
        items: List,
        page: int,
        page_size: int,
        page_callback_data_class: Type[PagedCallbackData],
        **page_kwargs,
) -> Tuple[List[InlineKeyboardButton], int]:
    buttons = []

    i = 0
    if page != 0:
        i += 1
        buttons.append(InlineKeyboardButton(
            text='◀',
            callback_data=page_callback_data_class(page=page - 1, **page_kwargs).pack()
        ))

    if len(items) == page_size + 1:
        i += 1
        buttons.append(InlineKeyboardButton(
            text='▶',
            callback_data=page_callback_data_class(page=page + 1, **page_kwargs).pack()
        ))
        items.pop()

    return buttons, i
