from enum import Enum

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class SretActions(Enum):
    SRET = 'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ'
    DRISHET = 'Я иду срать'
    PERNUL = 'Я закончил срать'
    END = 'Я просто пернул'


def get() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    for el in SretActions:
        kb.button(el)

    kb.adjust(2)

    return kb.as_markup()
