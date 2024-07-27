import sys

sys.path.append('..')

from datetime import datetime

from aiogram.types import BufferedInputFile
from tortoise.expressions import Q

from db.ToiletSessions import SretSession

import asyncio
import json

import aiormq
from aiogram import Bot
from aiormq.abc import DeliveredMessage
from loguru import logger

import config
import db
import setup_logger


setup_logger.__init__('Export Info Service')

bot: Bot

message_text = ('<b>Пояснение к столбцам таблице:</b>\n'
                ' - <i>start</i> — Время начала действия, часовой пояс: UTC\n'
                ' - <i>end</i> — Время конца действия, часовой пояс: UTC\n'
                ' - <i>autoend</i> — Имеет значени 1, если действие было завершено автоматически, иначе 0\n'
                ' - <i>sret_type</i> — Тип действия. 1 - Сранье, 2 - Дристание, 3 - Пердеж\n')


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())
    buffer = 'start,end,autoend,sret_type\n'

    async for session in SretSession.filter(user_id=body['user_id']).filter(~Q(end=None)).order_by('-start'):
        date_format = '%d.%m.%Y %H:%M:%S'
        row = f'{session.start.strftime(date_format)},{session.end.strftime(date_format)},{int(session.autoend)},{session.sret_type}\n'

        buffer += row

    io_csv = BufferedInputFile(buffer.encode(), filename=f'{body["user_id"]}_{int(datetime.now().timestamp())}.csv')
    try:
        export_message = await bot.send_document(body['send_to_user_id'], io_csv, caption='Экспортировали активность за все время.')
        await export_message.reply(message_text)

    except Exception as e:
        logger.info(f'Failed send exported info to {body["send_to_user_id"]} - error: {e}')

    await message.channel.basic_ack(message.delivery_tag)


async def main():
    global bot

    await db.init()

    bot = Bot(
        token=config.Telegram.token,
        parse_mode='html',
    )

    connection = await aiormq.connect(config.AMQP.uri)
    channel = await connection.channel()
    await channel.basic_qos(prefetch_count=1)

    declare = await channel.queue_declare('export_info', durable=True)
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
