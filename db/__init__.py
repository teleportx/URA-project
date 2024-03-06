import urllib.parse

from tortoise import Tortoise

from config import DB as cDB


async def init():
    await Tortoise.init(
        db_url=f'postgres://{cDB.user}:{urllib.parse.quote_plus(cDB.password)}@{cDB.host}:{cDB.port}/{cDB.db_name}',
        modules={'models': ['db.User', 'db.ToiletSessions']}
    )
