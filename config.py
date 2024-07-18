from asyncio import AbstractEventLoop
from os import environ

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import User
from dotenv import load_dotenv

load_dotenv()

DEBUG = environ.get('DEBUG') == "TRUE"

bot: Bot
bot_me: User
storage: RedisStorage
loop: AbstractEventLoop


class Telegram:
    token = environ.get('TOKEN')
    admin_token = environ.get('TOKEN_ADMIN')

    admin_group_id = environ.get('ADMIN_GROUP_ID')
    global_channel_id = environ.get('GLOBAL_CHANNEL_ID')


class Logger:
    max_file_size = 10 * 1024 ** 2


class Constants:
    group_members_limit = 21
    friends_limit = 53
    member_group_limit = 5

    srat_delete_time = 60 * 4  # in minutes

    throttling_time = 0.5  # in seconds
    throttling_time_actions = (  # in minutes
        (5, 2, 2),
        (2, 1, 1),
        (1, 1, 1),
    )  # row - last action, column - now action. See SretActions enum to get names.


class DB:
    host = environ.get('DB_HOST')
    port = int(environ.get('DB_PORT'))
    user = environ.get('DB_USER')
    password = environ.get('DB_PASSWORD')
    db_name = environ.get('DB_NAME')


class REDIS:
    host = environ.get('REDIS_HOST')
    port = int(environ.get('REDIS_PORT'))
    user = environ.get('REDIS_USER')
    password = environ.get('REDIS_PASSWORD')
    db_name = environ.get('REDIS_NAME')


class AMQP:
    host = environ.get('AMQP_HOST')
    port = int(environ.get('AMQP_PORT'))
    vhost = environ.get('AMQP_VHOST')
    user = environ.get('AMQP_USER')
    password = environ.get('AMQP_PASSWORD')

    uri = f'amqp://{user}:{password}@{host}:{port}/{vhost}'
