import sys

sys.path.append('..')

import asyncio
from datetime import datetime, timedelta

import pytz
from aiogram import Bot

import brocker
import config
import db
import setup_logger
from db.ToiletSessions import SretSession, SretType
from utils import send_srat_notification

setup_logger.__init__('Autoend Service')

autoend_sql = f'''
SELECT sretsession.*  FROM sretsession
         JOIN public."user" u on u.uid = sretsession.user_id
         WHERE (start <= (NOW() - interval '{config.Constants.srat_delete_time} minute') OR
               (start <= (NOW() - interval '1 min' * u.autoend_time) AND sretsession.autoend = true)) AND
               sret_type in {SretType.SRET.value, SretType.DRISHET.value} AND "end" IS NULL;
'''


async def end_loop():
    while True:
        # ORDER THIS 2 LINES IMPORTANT
        sessions = await SretSession.raw(autoend_sql)
        delete_time = datetime.now(pytz.UTC) - timedelta(minutes=config.Constants.srat_delete_time)

        for session in sessions:
            user = await session.user
            await config.bot.edit_message_reply_markup(user.uid, session.message_id, reply_markup=None)

            if delete_time >= session.start:
                await session.delete()

                try:
                    await config.bot.send_message(user.uid,
                                                  '<b>Вы умерли в туалете!</b>\n'
                                                  'Мы удалили вашу сессию сранья так как вы слишком долго срете, надеемся вы сейчас живы, и просто забыли завершить сранье, впредь будьте внимательнее.')
                except:
                    ...

                continue

            session.end = datetime.now(pytz.UTC)
            await session.save()

            await send_srat_notification.send(user, 0)

        await asyncio.sleep(60)


async def main():
    await brocker.init()

    await db.init()

    bot = Bot(
        token=config.Telegram.token,
        parse_mode='html',
    )
    config.bot = bot

    await end_loop()


if __name__ == "__main__":
    asyncio.run(main())
