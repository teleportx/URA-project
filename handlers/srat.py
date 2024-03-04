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


async def handle_first_srat(message: types.Message, user: User):
    if (await SretSession.filter(user=user).count()) == 0:
        await message.answer("*Впервые срете?*\n"
                             "Не забудьте вступить в группу для обсуждения вашего сранья, когда вы делаете это не одни."
                             "Для этого пропишите /link и вступите в группу, туда можно писать, только когда срешь.\n"
                             "Также не забывайте завершать свое сранье, иначе вас будут бить говяными розгами.",
                             parse_mode='markdown')


@router.message(F.text.startswith('Я'), UserAuthFilter(), F.chat.type == ChatType.PRIVATE)
async def send_srat(message: types.Message, user: User):
    must_not_sret = [
        'Я иду срать',
        'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ',
    ]

    must_sret = [
        'Я закончил срать',
    ]

    reply_markup = None

    if message.text in must_sret:
        if not await SretSession.filter(user=user, end=None).exists():
            await message.reply('Ты что заканчивать захотел? Ты даже не срешь!')
            return

    if message.text in must_not_sret:
        if await SretSession.filter(user=user, end=None).exists():
            await message.reply('Ты прошлое свое сранье не закончил, а уже новое начинаешь?\n'
                                'Нет уж. Будь добр, раз начал - закончи.')
            return

    await message.delete()

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

    if sret in [1, 2]:
        await handle_first_srat(message, user)
        reply_markup = cancel_autoend_srat_keyboard
        await SretSession.create(user=user, sret_type=SretType.DRISHET if sret == 2 else SretType.SRET)

    else:
        session = await SretSession.filter(user=user, end=None).get_or_none()

        if session is not None:
            session.end = datetime.now()
            if sret == 3:
                session.sret_type = SretType.PERNUL

            await session.save()

        else:
            await SretSession.create(user=user, end=datetime.now(), sret_type=SretType.PERNUL)

    try:
        permissions = ChatPermissions(can_send_messages=sret in [1, 2])
        await config.Telegram.bot.restrict_chat_member(config.Telegram.group_id, message.from_user.id, permissions)

    except aiogram.exceptions.TelegramBadRequest as e:
        if e.message != 'Bad Request: can\'t remove chat owner':
            raise e

    async for send_to in User.all():
        try:
            await config.Telegram.bot.send_message(send_to.uid, text % message.chat.full_name,
                                                   parse_mode='markdown',
                                                   reply_markup=reply_markup if send_to.uid == message.chat.id else None)

        except Exception as e:
            logging.warning(f'Cannnot send notify to {message.chat.id} cause: {e}')


@router.callback_query(F.data == 'cancel_srat')
async def cancel_srat(callback: types.CallbackQuery):
    await callback.answer('Отменили автозавершение.')
    await callback.message.edit_reply_markup()
