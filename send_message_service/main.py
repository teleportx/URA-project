import sys

sys.path.append('..')

import asyncio
import json
import time

import aiormq
from aiogram import Bot
from aiormq.abc import DeliveredMessage
from loguru import logger

import config
import db
import setup_logger
from db.Notify import Notify

setup_logger.__init__('Send Message Service')

bot: Bot

update_notify_counter_sql = 'UPDATE notify SET executed_users_count = executed_users_count + 1 WHERE message_id = %d;'


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    try:
        func = bot.copy_message
        if body.get('show_sender', False):
            func = bot.forward_message

        await func(body['send_to'], body['forward_message_chat'], body['forward_message'])

        logger.debug(f'Sended message to {body["send_to"]} from chat {body["forward_message_chat"]} message {body["forward_message"]}.')

    except Exception as e:
        logger.info(f'Cannnot send notify to {body["send_to"]} cause: {e}')

    if body['notify_id'] is not None:
        await Notify.raw(update_notify_counter_sql % body['notify_id'])

    await message.channel.basic_ack(message.delivery_tag)
    time.sleep(0.066)  # costyl? | Message sending rate limiter


async def main():
    global bot

    await db.init()

    bot = Bot(
        token=config.Telegram.token,
        parse_mode='markdown',
    )

    connection = await aiormq.connect(config.AMQP.uri)
    channel = await connection.channel()
    await channel.basic_qos(prefetch_count=1)

    declare = await channel.queue_declare('send_message', durable=True, arguments={"x-max-priority": 10})
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
