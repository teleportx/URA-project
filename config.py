from os import environ

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

DEBUG = environ.get('DEBUG') == "TRUE"
bot: Bot


class Telegram:
    token = environ.get('TOKEN')


class Logger:
    max_file_size = 10 * 1024 ** 2


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
