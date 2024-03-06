from enum import Enum

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class SretActions(Enum):
    SRET = 'Я иду срать'
    DRISHET = 'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ'
    PERNUL = 'Я просто пернул'
    END = 'Я закончил срать'


def get() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    for el in SretActions:
        kb.button(text=el.value)

    kb.adjust(2)

    return kb.as_markup()
