import json

from loguru import logger

from . import base


async def export_info(send_to: int, user_id: int):
    channel = await (await base.storer.get_connection()).channel()

    body = json.dumps({
        "send_to_user_id": send_to,
        "user_id": user_id,

    }, separators=(',', ':')).encode()

    await channel.basic_publish(
        body,
        routing_key='export_info',
    )

    logger.debug(f'Booked export info to {send_to} user_id {user_id}.')

