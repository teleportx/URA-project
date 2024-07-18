from aiogram import Router, Bot
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
from db.User import User
from keyboards import whois_keyboard

router = Router()

report_bot = Bot(
    token=config.Telegram.admin_token,
    parse_mode='html',
)


class SendReport(StatesGroup):
    writing_report = State()


@router.message(Command("report"))
async def report(message: types.Message, state: FSMContext):
    text = ('Здесь вы можете написать сообщение администрации. Сообщайте о багах, о нарушении правил использования бота, о предложениях к функционалу и т. д.\n'
            'Напишите следующим сообщением то, что вы хотите отправить нам.\n\n'
            'Для отмены используйте команду /cancel')

    await message.delete()
    await state.set_state(SendReport.writing_report)

    last_msg = await message.answer(text)
    await state.update_data(last_msg=last_msg.message_id)


@router.message(SendReport.writing_report)
async def writing_report(message: types.Message, state: FSMContext, user: User):
    await state.clear()
    await message.reply('Ваша обращение зафиксировано!')

    await report_bot.send_message(config.Telegram.admin_group_id,
                                  f'❗️<b>Зафикисировано обращение</b>\n'
                                  f'От: _{user.name}_ (`{user.uid}`)',
                                  reply_markup=whois_keyboard.get(user.uid))

    await report_bot.send_message(config.Telegram.admin_group_id, message.text, entities=message.entities, parse_mode=None)
