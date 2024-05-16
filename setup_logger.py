import gzip
import logging
import os
import platform
from datetime import datetime
from pathlib import Path

from aiogram import Bot
from aiogram.types import BufferedInputFile
from loguru import logger

import config

project_name: str


class InterceptHandler(logging.Handler):
    LEVELS_MAP = {
        logging.CRITICAL: "CRITICAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARNING",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
    }

    def _get_level(self, record):
        return self.LEVELS_MAP.get(record.levelno, record.levelno)

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(exception=record.exc_info).log(level, record.getMessage())


class TelegramHandler(logging.Handler):
    def __init__(self):
        super().__init__()

        self.bot = Bot(
            token=config.Telegram.logs_token,
            parse_mode='markdown',
        )

    async def _send_notification(self, record: logging.LogRecord):
        text = (f'⚠️ *{record.levelname} | {project_name}*\n\n'
                f'Caught log in file.')

        try:
            io_log = BufferedInputFile(record.getMessage().encode(), filename=f'{datetime.now()}.log')
            await self.bot.send_document(config.Telegram.admin_group_id, io_log, caption=text)

        except Exception as e:
            print(':CRITICAL: ERROR WHILE SENDING LOGS TO TG: ')
            print(e)

    def emit(self, record: logging.LogRecord):
        config.loop.create_task(self._send_notification(record))


def __init__(__project_name: str):
    global project_name

    project_name = __project_name
    project_name_u = project_name.replace(" ", "-").lower()

    logs_dir_path = Path(__file__).resolve().__str__().replace('setup_logger.py', 'logs')
    if not os.path.exists(logs_dir_path):
        os.mkdir(logs_dir_path)

    if os.path.exists(f'{logs_dir_path}/latest-{project_name_u}.log'):
        os.remove(f'{logs_dir_path}/latest-{project_name_u}.log')

    for log_file in os.listdir(logs_dir_path):
        if not log_file.endswith('.log') or project_name_u not in log_file:
            continue

        with open(f'{logs_dir_path}/{log_file}', 'rb') as fp:
            log_bytes = fp.read()

        with open(f'{logs_dir_path}/{log_file}.gz', 'wb') as fp:
            fp.write(gzip.compress(log_bytes))

        os.remove(f'{logs_dir_path}/{log_file}')

    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    logging.getLogger('aiogram').addHandler(InterceptHandler())
    logging.getLogger('asyncio').setLevel(logging.DEBUG)
    logging.getLogger('asyncio').addHandler(InterceptHandler())

    logger.add(f'{logs_dir_path}/URA-{project_name_u}_' + '{time:YYYY-MM-DD_hh:mm:ss!UTC}.log',
               rotation='00:00',
               compression='gz')

    logger.add(f'{logs_dir_path}/latest-{project_name_u}.log')

    logger.info(f'URA-PROJECT | {project_name}')
    if config.DEBUG:
        logger.warning('APP IN DEBUG MODE')

    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")

    if not config.DEBUG:
        logger.add(TelegramHandler(), level=logging.ERROR)
