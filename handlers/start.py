from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from filters.user import UserAuthFilter

router = Router()


@router.message(Command("start"), UserAuthFilter())
async def start(message: types.Message):
    kb = ReplyKeyboardBuilder()

    kb.button(text='Я иду ЛЮТЕЙШЕ ДРИСТАТЬ')
    kb.button(text='Я иду срать')
    kb.button(text='Я закончил срать')
    kb.button(text='Я просто пернул')

    kb.adjust(2)

    await message.reply('Выберете действие.', reply_markup=kb.as_markup())


@router.message(Command("start"), UserAuthFilter(auth=False))
async def start_unauth(message: types.Message):
    await message.reply('Извините, вы не можете уведомлять всех о том, что вы идете срать.\n\n'
                        'Если вы все же хотите это делать, напишите администратору бота с просьбой об этом.\n'
                        f'*Ваш id:* `{message.chat.id}`',
                        parse_mode='markdown')
