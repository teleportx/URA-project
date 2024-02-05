import logging
from datetime import datetime

import aiogram
from aiogram import types, Router, F
from aiogram.enums import ChatType
from aiogram.types import ChatPermissions

import config
from db.User import User, SretSession
from filters.user import UserAuthFilter

router = Router()


async def handle_first_srat(message: types.Message, user: User):
    if SretSession.select().where(SretSession.user == user).count() == 0:
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

    if message.text in must_sret:
        if user.sret is None:
            await message.reply('Ты что заканчивать захотел? Ты даже не срешь!')
            return

    if message.text in must_not_sret:
        if user.sret is not None:
            await message.reply('Ты прошлое свое сранье не закончил, а уже новое начинаешь?\n'
                                'Нет уж. Будь добр, раз начал - закончи.')
            return

    await message.delete()

    if message.text == 'Я иду срать':
        text = '⚠️ *ВНИМАНИЕ* ⚠️\n' \
               '`%s` *прямо сейчас* пошел _срать_'
        sret = True

    elif message.text == 'Я закончил срать':
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '`%s` закончил _срать_'
        sret = False

    elif message.text == 'Я просто пернул':
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '`%s` просто _пернул_'
        sret = False

    elif message.text == 'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ':
        text = '⚠️️️️⚠️⚠️ ВНИМАНИЕ ⚠️⚠️⚠️\n\n' \
               '⚠️НАДВИГАЕТСЯ *ГОВНОПОКАЛИПСИС*⚠️\n' \
               '`%s` *прямо сейчас* пошел _адски дристать_ лютейшей струей *поноса*'
        sret = True

    else:
        return

    if user.sret is not None and not sret:
        SretSession.create(user=user, start=user.sret)

    if sret:
        await handle_first_srat(message, user)

    user.sret = datetime.now() if sret else None
    user.save()

    try:
        permissions = ChatPermissions(can_send_messages=sret)
        await config.Telegram.bot.restrict_chat_member(config.Telegram.group_id, message.from_user.id, permissions)

    except aiogram.exceptions.TelegramBadRequest as e:
        if e.message != 'Bad Request: can\'t remove chat owner':
            raise e

    for send_to in User.select():
        try:
            await config.Telegram.bot.send_message(send_to.uid, text % message.chat.full_name,
                                                   parse_mode='markdown')

        except Exception as e:
            logging.warning(f'Cannnot send notify to {message.chat.id} cause: {e}')
