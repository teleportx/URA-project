from aiogram import Bot
from aiogram.filters import Command, BaseFilter
from aiogram.filters.command import CommandException
from aiogram.types import Message

import config


class CommandMention(BaseFilter):
    def __init__(self, *args, **kwargs):
        self.command = Command(*args, **kwargs)

    async def __call__(self, message: Message, bot: Bot):
        ping = f'@{config.bot_me.username}'

        text = message.text
        if text is None:
            text = ''

        if text.startswith(ping):
            text = ' '.join(message.text.split()[1:])

        try:
            command = await self.command.parse_command(text=text, bot=bot)

        except CommandException:
            return False

        return {'command': command}
