import json

from aiogram import Router
from aiogram import types
from aiogram.filters import CommandObject
from aiogram.utils.formatting import Text, Pre, Code
from loguru import logger

import config
from main_service.filters import CommandMention
from main_service.filters import UserAuthFilter
from middlewares.degrade import DegradationData

router = Router()


def render_now_degradations(degrade_model: DegradationData):
    rer = degrade_model.__str__().replace(" ", "\n")
    return Pre(rer, language='Текущий статус деградаций')


@router.message(CommandMention("degrade"), UserAuthFilter(admin=True))
async def degrade(message: types.Message, command: CommandObject):
    args = [''] if command.args is None else command.args.split()

    degrade_now = json.loads(await config.storage.redis.get('degrade'))
    if args[0] in DegradationData.model_fields:
        degrade_now[args[0]] = not degrade_now[args[0]]

        logger.warning(f'{message.from_user.id} SET DEGRADATION MODE {args[0]}={degrade_now[args[0]]}')

    degrade_model = DegradationData(**degrade_now)

    if args[0] not in DegradationData.model_fields:
        degradation_keys = []
        for el in DegradationData.model_fields.keys():
            degradation_keys.append(Code(el))
            degradation_keys.append(', ')
        degradation_keys.pop()

        text = Text(
            f'Не можем найти деградацию ', Code(args[0]), '\n',
            f'Возможные деградации: ', *degradation_keys, '\n\n',
            render_now_degradations(degrade_model),
        )
        await message.reply(**text.as_kwargs())
        return

    await config.storage.redis.set('degrade', json.dumps(degrade_model.model_dump()))

    await message.reply(**Text('Успешно', render_now_degradations(degrade_model)).as_kwargs())
