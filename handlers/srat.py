import logging
from datetime import datetime

import aiogram
from aiogram import types, Router, F
from aiogram.enums import ChatType
from aiogram.types import ChatPermissions, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from db.User import User
from db.ToiletSessions import SretSession, SretType
from filters.user import UserAuthFilter

router = Router()

cancel_autoend_srat_keyboard = InlineKeyboardBuilder([[
    InlineKeyboardButton(text='Отменить автозавершение сранья', callback_data='cancel_srat')
]]).as_markup()


@router.message(F.text.startswith('Я'), UserAuthFilter(), F.chat.type == ChatType.PRIVATE)
async def send_srat(message: types.Message, user: User):
    must_not_sret = [1, 2]
    must_sret = [0]

    if message.text == 'Я иду срать':
        text = '⚠️ *ВНИМАНИЕ* ⚠️\n' \
               '`%s` *прямо сейчас* пошел _срать_'
        sret = 1

    elif message.text == 'Я закончил срать':
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '`%s` закончил _срать_'
        sret = 0

    elif message.text == 'Я просто пернул':
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '`%s` просто _пернул_'
        sret = 3

    elif message.text == 'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ':
        text = '⚠️️️️⚠️⚠️ ВНИМАНИЕ ⚠️⚠️⚠️\n\n' \
               '⚠️НАДВИГАЕТСЯ *ГОВНОПОКАЛИПСИС*⚠️\n' \
               '`%s` *прямо сейчас* пошел _адски дристать_ лютейшей струей *поноса*'
        sret = 2

    else:
        return

    if sret in must_sret:
        if not await SretSession.filter(user=user, end=None).exists():
            await message.reply('Ты что заканчивать захотел? Ты даже не срешь!')
            return

    if sret in must_not_sret:
        if await SretSession.filter(user=user, end=None).exists():
            await message.reply('Ты прошлое свое сранье не закончил, а уже новое начинаешь?\n'
                                'Нет уж. Будь добр, раз начал - закончи.')
            return

    await message.delete()

    # Send self
    self_message = await message.answer(text % message.chat.full_name,
                                        reply_markup=cancel_autoend_srat_keyboard if sret in must_not_sret else None)

    # DB operations
    if sret in must_not_sret:
        await SretSession.create(message_id=self_message.message_id, user=user,
                                 sret_type=SretType.DRISHET if sret == 2 else SretType.SRET)

    else:
        session = await SretSession.filter(user=user, end=None).get_or_none()

        if session is not None:
            session.end = datetime.now()
            session.autoend = False
            if sret == 3:
                session.sret_type = SretType.PERNUL

            await session.save()
            try:
                await config.Telegram.bot.edit_message_reply_markup(message.chat.id, session.message_id)

            except aiogram.exceptions.TelegramBadRequest:
                ...

        else:
            await SretSession.create(message_id=self_message.message_id, user=user, end=datetime.now(),
                                     sret_type=SretType.PERNUL, autoend=False)

    # Send notifications
    users_send = set()
    users_send += set(await User.all().only('uid'))
    users_send.remove(user)

    for send_to in users_send:
        try:
            await config.Telegram.bot.send_message(send_to.uid, text % message.chat.full_name)

        except Exception as e:
            logging.info(f'Cannnot send notify to {message.chat.id} cause: {e}')


@router.callback_query(F.data == 'cancel_srat')
async def cancel_srat(callback: types.CallbackQuery):
    await SretSession.filter(message_id=callback.message.message_id).update(autoend=False)

    await callback.answer('Отменили автозавершение.')
    await callback.message.edit_reply_markup()
