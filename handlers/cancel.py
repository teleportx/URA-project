import asyncio

from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import config

router = Router()


@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    last_msg = (await state.get_data()).get('last_msg')
    await state.clear()

    info_message = await message.reply('Отменили.')
    if last_msg is not None:
        await config.bot.delete_message(message.chat.id, last_msg)

    await asyncio.sleep(3)
    await message.delete()
    await info_message.delete()
