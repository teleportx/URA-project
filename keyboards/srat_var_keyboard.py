from enum import Enum

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class SretActions(Enum):
    SRET = (1, 'Я иду срать')
    DRISHET = (2, 'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ')
    PERNUL = (3, 'Я просто пернул')
    END = (0, 'Я закончил срать')


def get() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    for el in SretActions:
        kb.button(text=el.value[1])

    kb.adjust(2)

    return kb.as_markup()
