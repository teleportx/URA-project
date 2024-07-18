from datetime import datetime

import aiogram.exceptions
import pytz
from loguru import logger

import config
from brocker import message_sender
from db.ToiletSessions import SretSession, SretType
from db.User import User
from keyboards import sret_keyboard

must_not_sret = [1, 2]
must_sret = [0]


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

    # Sending to global
    global_message = await config.bot.send_message(config.Telegram.global_channel_id, text)

    for send_to in users_send:
        await message_sender.send_message(send_to.uid, global_message.chat.id, global_message.message_id, 1)

    return self_message.message_id
