import sys

from loguru import logger

sys.path.append('..')

import asyncio
import json

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

import brocker
import config
import db
import handlers
import middlewares
import setup_logger
from middlewares.degrade import DegradationData

setup_logger.__init__('Bot Service')

redis_url = f'redis://{config.REDIS.user}:{config.REDIS.password}@{config.REDIS.host}:{config.REDIS.port}/{config.REDIS.db_name}'
storage = RedisStorage.from_url(redis_url)
dp = Dispatcher(storage=storage)

bot = Bot(
    token=config.Telegram.token,
    parse_mode='html',
)
config.bot = bot


async def main():
    await db.init()
    await brocker.init()

    config.storage = storage
    await storage.redis.set('degrade', json.dumps(DegradationData().model_dump()), nx=True)

    config.bot_me = await bot.me()
    config.loop = asyncio.get_running_loop()

    middlewares.setup(dp)

    dp.include_router(handlers.router)

    if config.DEBUG:
        await bot.delete_webhook()
        await dp.start_polling(bot)
        return

    logger.info('Setting webhook...')
    await bot.set_webhook(f"{config.Webhook.remote_host}{config.Webhook.path}", secret_token=config.Webhook.secret)


if __name__ == "__main__":
    if config.DEBUG:
        asyncio.run(main())

    else:
        dp.startup.register(main)

        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=config.Webhook.secret,
        )

        webhook_requests_handler.register(app, path=config.Webhook.path)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host=config.Webhook.host, port=config.Webhook.port)

