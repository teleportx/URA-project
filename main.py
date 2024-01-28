import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
import handlers
import middlewares

logging.basicConfig(level=logging.INFO)

werkzeug = logging.getLogger('werkzeug')
werkzeug.setLevel(config.logging_level)

aiogram_event = logging.getLogger('aiogram.event')
aiogram_event.setLevel(config.logging_level)


async def main():
    bot = Bot(token=config.Telegram.token)
    config.Telegram.bot = bot

    dp = Dispatcher()
    middlewares.setup(dp)

    dp.include_router(handlers.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
