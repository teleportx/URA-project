import asyncio
import json

import aiormq
from aiogram import Bot
from aiormq.abc import DeliveredMessage
from loguru import logger

import config
import setup_logger

setup_logger.__init__('Send Message Service')

bot: Bot


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    try:
        await bot.copy_message(body['send_to'], body['forward_message_chat'], body['forward_message'])

        logger.debug(f'Sended message to {body["send_to"]} from chat {body["forward_message_chat"]} message {body["forward_message"]}.')

    except Exception as e:
        logger.info(f'Cannnot send notify to {body["send_to"]} cause: {e}')

    await message.channel.basic_ack(message.delivery_tag)


async def main():
    global bot
    bot = Bot(
        token=config.Telegram.token,
        parse_mode='markdown',
    )

    connection = await aiormq.connect(config.AMQP.uri)
    channel = await connection.channel()

    declare = await channel.queue_declare('send_message')
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
