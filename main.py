import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

import config
import db
import handlers
import middlewares
import setup_logger

setup_logger.__init__('Bot Service')


async def main():
    await db.init()

    redis_url = f'redis://{config.REDIS.user}:{config.REDIS.password}@{config.REDIS.host}:{config.REDIS.port}/{config.REDIS.db_name}'
    storage = RedisStorage.from_url(redis_url)

    bot = Bot(
        token=config.Telegram.token,
        parse_mode='markdown',
    )
    config.bot = bot

    dp = Dispatcher(storage=storage)
    middlewares.setup(dp)

    dp.include_router(handlers.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
