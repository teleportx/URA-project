import asyncio
import json

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

import brocker
import config
import db
import handlers
import middlewares
import setup_logger
from middlewares.degrade import DegradationData

setup_logger.__init__('Main Service')


async def main():
    await db.init()

    await brocker.init()

    redis_url = f'redis://{config.REDIS.user}:{config.REDIS.password}@{config.REDIS.host}:{config.REDIS.port}/{config.REDIS.db_name}'
    storage = RedisStorage.from_url(redis_url)
    config.storage = storage

    await storage.redis.set('degrade', json.dumps(DegradationData().model_dump()), nx=True)

    bot = Bot(
        token=config.Telegram.token,
        parse_mode='markdown',
    )
    config.bot = bot
    config.bot_me = await bot.me()
    config.loop = asyncio.get_running_loop()

    dp = Dispatcher(storage=storage)
    middlewares.setup(dp)

    dp.include_router(handlers.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
