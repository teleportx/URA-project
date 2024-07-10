import aiormq

import config

from . import base


async def init():
    base.connection = await aiormq.connect(config.AMQP.uri)
    channel = await base.connection.channel()

    await channel.queue_declare("send_message")
