from aiogram.filters import BaseFilter
from aiogram.types import Message


class CommandArgsStartswith(BaseFilter):
    def __init__(self, prefix: str = None):
        self.prefix = prefix

    async def __call__(self, message: Message):
        if self.prefix is None:
            return len(message.text.split(' ')) == 1

        try:
            return message.text.split(' ')[1].startswith(self.prefix)

        except IndexError:
            return False
