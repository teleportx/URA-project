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

ISC = '⠀'  # INVISIBLE SPACE CHAR


class Telegram:
    token = environ.get('TOKEN')
    logs_token = environ.get('TOKEN_LOGS')

    logs_group_id = environ.get('LOGS_GROUP_ID')
    global_channel_id = environ.get('GLOBAL_CHANNEL_ID')


class Logger:
    max_file_size = 10 * 1024 ** 2


class Constants:
    group_members_limit = 21
    member_group_limit = 5

    srat_delete_time = 1  # in hours
    srat_autoend_time = 10  # in minutes

    throttling_time = 1  # in seconds


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
