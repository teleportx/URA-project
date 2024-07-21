from datetime import datetime, timedelta
from typing import Optional

import aiogram.exceptions
import pytz
from aiogram import types
from loguru import logger

import config
from brocker import message_sender
from db.ToiletSessions import SretSession, SretType
from db.User import User
from keyboards import sret_keyboard

must_not_sret = [1, 2]
must_sret = [0]


async def verify_action(user: User, sret: int, message: Optional[types.Message] = None):
    last_session = await SretSession.filter(user=user).order_by('-message_id').first()

    has_opened_session = False
    if last_session is not None:
        has_opened_session = last_session.end is None

    if sret in must_sret and not has_opened_session:
        if message is not None:
            await message.reply('Ты что заканчивать захотел? Ты даже не срешь!')
        return False

    if sret in must_not_sret and has_opened_session:
        if message is not None:
            await message.reply('Ты прошлое свое сранье не закончил, а уже новое начинаешь?\n'
                                'Нет уж. Будь добр, раз начал - закончи.')
        return False

    if has_opened_session or last_session is None:
        return True

    throttling_time = timedelta(minutes=config.Constants.throttling_time_actions[last_session.sret_type - 1][sret - 1])
    now = datetime.now(pytz.UTC).astimezone()
    if (now - last_session.end) <= throttling_time:
        if message is not None:
            wait_time = round((throttling_time - (now - last_session.end)).total_seconds())
            await message.reply(f'Вы совершаете действия слишком часто!\n'
                                f'Подождите еще <b>{wait_time} секунд</b>')
        return False

    return True


def get_message_text(user: User, sret: int):
    if sret == 1:
        text = '⚠️ <b>ВНИМАНИЕ</b> ⚠️\n' \
               '<code>%s</code> <b>прямо сейчас</b> пошел <i>срать</i>'

    elif sret == 0:
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '<code>%s</code> закончил <i>срать</i>'

    elif sret == 3:
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '<code>%s</code> просто <i>пернул</i>'

    elif sret == 2:
        text = '⚠️️️️⚠️⚠️ ВНИМАНИЕ ⚠️⚠️⚠️\n\n' \
               '⚠️НАДВИГАЕТСЯ <b>ГОВНОПОКАЛИПСИС</b>⚠️\n' \
               '<code>%s</code> <b>прямо сейчас</b> пошел <i>адски дристать</i> лютейшей струей <b>поноса</b>'

    text %= user.name

    return text


async def send(user: User, sret: int):
    text = get_message_text(user, sret)

    # Send self
    self_message = await config.bot.send_message(user.uid, text,
                                                 reply_markup=sret_keyboard.get(user.autoend) if sret in must_not_sret else None)

    # DB operations
    if sret in must_not_sret:
        await SretSession.create(message_id=self_message.message_id, user=user,
                                 sret_type=SretType.DRISHET if sret == 2 else SretType.SRET,
                                 autoend=user.autoend)

    else:
        session = await SretSession.filter(user=user, end=None).first()

        if session is not None:
            session.end = datetime.now()
            session.autoend = False
            if sret == 3:
                session.sret_type = SretType.PERNUL

            await session.save()
            try:
                await config.bot.edit_message_reply_markup(user.uid, session.message_id)

            except aiogram.exceptions.TelegramBadRequest:
                ...

        else:
            await SretSession.create(message_id=self_message.message_id, user=user, end=datetime.now(pytz.UTC),
                                     sret_type=SretType.PERNUL, autoend=False)

    # Send notifications
    users_send = set()

    group_query = user.groups_member
    if sret == 3:
        group_query = group_query.filter(notify_perdish=True)
    async for group in group_query:
        users_send = users_send.union(set(await group.members.all()))

    users_send = users_send.union(set(await user.friends.all()))

    try:
        users_send.remove(user)

    except KeyError:
        ...

    await message_sender.send_message(config.Telegram.global_channel_id, user.uid, self_message.message_id, 1)
    for send_to in users_send:
        await message_sender.send_message(send_to.uid, user.uid, self_message.message_id, 1)

    return self_message.message_id
