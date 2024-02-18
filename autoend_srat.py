import asyncio
import logging
from datetime import datetime

import aiogram
from aiogram.types import ChatPermissions

import config
from db.User import User, SretSession
from db.base import db

tasks = {}


async def end_srat(user: User):
    await asyncio.sleep(10 * 60 - (datetime.now() - user.sret).total_seconds())

    with db:
        SretSession.create_session(user)
        user.sret = None
        user.save()

    name = (await config.Telegram.bot.get_chat(user.uid)).full_name

    try:
        permissions = ChatPermissions(can_send_messages=False)
        await config.Telegram.bot.restrict_chat_member(config.Telegram.group_id, user.uid, permissions)

    except aiogram.exceptions.TelegramBadRequest as e:
        if e.message != 'Bad Request: can\'t remove chat owner':
            raise e

    with db:
        for send_to in User.select():
            try:
                await config.Telegram.bot.send_message(send_to.uid,
                                                       f'⚠️ ВНИМАНИЕ ⚠️\n`{name}` закончил _срать_',
                                                       parse_mode='markdown')

            except Exception as e:
                logging.warning(f'Cannnot send notify to {user.uid} cause: {e}')


async def create_srat_task(user: User):
    task = asyncio.create_task(end_srat(user))
    tasks.update({user.uid: task})
