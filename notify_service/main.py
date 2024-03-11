import asyncio

from aiogram import Bot
from loguru import logger
from tortoise.functions import Count

import config
import db
import setup_logger
from db.User import Notify

setup_logger.__init__('Notify Service')


async def notify_loop(bot: Bot):
    while True:
        notifys = Notify.annotate(queue_count=Count('queue')).filter(queue_count__not=0).order_by('created_at')

        async for notify in notifys:
            async for send_to in notify.queue.all():
                try:
                    await bot.copy_message(send_to.uid, (await notify.initiated_by).uid, notify.message_id)

                except Exception as e:
                    notify.errors += 1
                    await notify.save()

                    logger.info(f"Can't send notification `{notify.pk}` to `{send_to.pk}` because {e}")

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
