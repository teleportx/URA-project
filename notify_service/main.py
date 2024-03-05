import asyncio
import logging

from aiogram import Bot
from tortoise.functions import Count

import config
import db
from db.User import Notify

logging.basicConfig(level=logging.INFO)

werkzeug = logging.getLogger('werkzeug')
werkzeug.setLevel(config.logging_level)

aiogram_event = logging.getLogger('aiogram.event')
aiogram_event.setLevel(config.logging_level)


async def notify_loop(bot: Bot):
    while True:
        notifys = Notify.annotate(queue_count=Count('queue')).filter(queue_count__not=0).order_by('created_at')

        async for notify in notifys:
            async for send_to in notify.queue.all():
                try:
                    await bot.send_message(send_to.uid, notify.text)

                except Exception as e:
                    notify.errors += 1
                    await notify.save()

                    logging.info(f"Can't send notification `{notify.pk}` to `{send_to.pk}` because {e}")

                await notify.queue.remove(send_to)
                await asyncio.sleep(2)

        await asyncio.sleep(120)


async def main():
    await db.init()

    bot = Bot(
        token=config.Telegram.token,
        parse_mode='markdown',
    )

    await notify_loop(bot)


if __name__ == "__main__":
    asyncio.run(main())
