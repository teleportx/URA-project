import json

from aiogram import Router
from aiogram import types
from aiogram.filters import CommandObject
from loguru import logger

import config
from config import ISC
from filters.command_mention import CommandMention
from filters.user import UserAuthFilter
from middlewares.degrade import DegradationData

router = Router()


def render_now_degradations(degrade_model: DegradationData):
    rer = degrade_model.__str__().replace(" ", "\n")
    return f'```Текущий{ISC}статус{ISC}деградаций\n{rer}```'


@router.message(CommandMention("degrade"), UserAuthFilter(admin=True))
async def degrade(message: types.Message, command: CommandObject):
    args = [''] if command.args is None else command.args.split()

    degrade_now = json.loads(await config.storage.redis.get('degrade'))
    if args[0] in DegradationData.model_fields:
        degrade_now[args[0]] = not degrade_now[args[0]]

        logger.warning(f'{message.from_user.id} SET DEGRADATION MODE {args[0]}={degrade_now[args[0]]}')

    degrade_model = DegradationData(**degrade_now)

    if args[0] not in DegradationData.model_fields:
        degradation_keys = [f'`{el}`' for el in DegradationData.model_fields.keys()]
        await message.reply(f'Не можем найти деградацию `{args[0]}`\n'
                            f'Возможные деградации: {", ".join(degradation_keys)}\n\n'
                            f'{render_now_degradations(degrade_model)}')
        return

    await config.storage.redis.set('degrade', json.dumps(degrade_model.model_dump()))

    await message.reply(f'Успешно\n{render_now_degradations(degrade_model)}')
