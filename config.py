from asyncio import AbstractEventLoop
from os import environ

from aiogram import Bot
from aiogram.types import User
from dotenv import load_dotenv

load_dotenv()

DEBUG = environ.get('DEBUG') == "TRUE"
bot: Bot
bot_me: User
loop: AbstractEventLoop


class Telegram:
    token = environ.get('TOKEN')
    logs_token = environ.get('TOKEN_LOGS')

    logs_group_id = environ.get('LOGS_GROUP_ID')


class Logger:
    max_file_size = 10 * 1024 ** 2


class Constants:
    group_members_limit = 21
    member_group_limit = 5

    srat_delete_time = 1  # in hours
    srat_autoend_time = 10  # in minutes


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
