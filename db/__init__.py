import urllib.parse

from tortoise import Tortoise

from config import DB as cDB


TORTOISE_ORM = {
    "connections": {"default": f"postgres://{cDB.user}:{urllib.parse.quote_plus(cDB.password)}@{cDB.host}:{cDB.port}/{cDB.db_name}"},
    "apps": {
        "models": {
            "models": ['db.User', 'db.ToiletSessions', 'db.UserUnion', 'db.Notify', 'db.ApiAuth', 'aerich.models'],
            "default_connection": "default",
        },
    },
}


async def init():
    await Tortoise.init(
        db_url=TORTOISE_ORM['connections']['defaul'],
        modules={"models": TORTOISE_ORM['apps']['models']['models']}
    )
