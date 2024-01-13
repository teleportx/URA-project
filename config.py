import os.path
from os import environ

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

data_file = 'data.json'
if not os.path.exists(data_file):
    with open(data_file, 'w+') as fp:
        fp.write('[]')


class Telegram:
    token = environ.get('TOKEN')
    bot: Bot
