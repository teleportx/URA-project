from datetime import datetime

from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject

import config
from brocker.export_info import export_info
from db.User import User

router = Router()


@router.message(Command("export"))
async def export(message: types.Message, command: CommandObject, user: User):
    user_id = user.uid
    if user.admin and command.args is not None and command.args.isnumeric():
        user_id = int(command.args)

    if not user.admin:
        key = f'{user.uid}_export'
        last_export = await config.storage.redis.get(key)
        if last_export is None:
            last_export = 0
        last_export = int(last_export)

        now = int(datetime.now().timestamp())

        if (now - last_export) < config.Constants.export_info_interval:
            await message.answer('Вы можете запрашивать экспорт информации не чаще чем раз в неделю.')
            return

        await config.storage.redis.set(key, now)

    await export_info(user.uid, user_id)
    await message.answer('Экспорт информации запрошен. Ожидайте.')
