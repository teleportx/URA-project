from . import base


async def init():
    await (await base.storer.get_connection()).channel()
