import json
import os.path
from os import environ

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

data_file = 'data.json'
if not os.path.exists(data_file):
    with open(data_file, 'w+') as fp:
        fp.write('[]')
with open(data_file, 'rb') as fp:
    _users = json.load(fp)


class Telegram:
    token = environ.get('TOKEN')
    bot: Bot

    users = _users
    admins = [306627312, 936638952]
