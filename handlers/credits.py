from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions

router = Router()


@router.message(Command("credits"))
async def credit(message: types.Message):
    text = (f'*УРА - Уведомление Ректальных Активностей*\n'
            f'Бот, чтобы держать всех вкурсе о ваших ректальных деяниях.\n'
            f'\n'
            f'```История\n'
            f'Идея бота возникла внезапно и первая версия бота была сделана в 2 файла, особо не заморчиваясь. '
            f'Затем проект обретал новые функции, фишки и все это вылилось в большую штуку под названием УРА.'
            f'```\n\n'
            f'Разработчик - [Teleport](https://github.com/teleportx/)\n'
            f'Автор идеи - [Алексей Шаблыкин](https://t.me/AllShabCH)\n'
            f'DevOps - [uuuuuno](https://github.com/uuuuuno/)\n')

    await message.answer(text, link_preview_options=LinkPreviewOptions(is_disabled=True))
