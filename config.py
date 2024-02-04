import logging
from os import environ

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

DEBUG = environ.get('DEBUG') == "TRUE"
logging_level = logging.WARN if not DEBUG else logging.DEBUG


class Telegram:
    token = environ.get('TOKEN')
    group_id = int(environ.get('GROUP_ID'))
    bot: Bot


class DB:
    host = environ.get('DB_HOST')
    port = int(environ.get('DB_PORT'))
    user = environ.get('DB_USER')
    password = environ.get('DB_PASSWORD')
    db_name = environ.get('DB_NAME')
