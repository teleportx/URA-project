import aiormq

import config

from . import base


async def init():
    base.connection = await aiormq.connect(config.AMQP.uri)
    await base.connection.channel()
