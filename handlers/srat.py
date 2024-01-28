import logging

from aiogram import types, Router, F

import config
from db.User import User
from filters.user import UserAuthFilter

router = Router()


@router.message(F.text.startswith('Я'), UserAuthFilter())
async def send_srat(message: types.Message):
    await message.delete()

    if message.text == 'Я иду срать':
        text = '⚠️ *ВНИМАНИЕ* ⚠️\n' \
               '`%s` *прямо сейчас* пошел _срать_'

    elif message.text == 'Я закончил срать':
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '`%s` закончил _срать_'

    elif message.text == 'Я просто пернул':
        text = '⚠️ ВНИМАНИЕ ⚠️\n' \
               '`%s` просто _пернул_'

    elif message.text == 'Я иду ЛЮТЕЙШЕ ДРИСТАТЬ ПОНОСОМ':
        text = '⚠️️️️⚠️⚠️ ВНИМАНИЕ ⚠️⚠️⚠️\n\n' \
               '⚠️НАДВИГАЕТСЯ *ГОВНОПОКАЛИПСИС*⚠️\n' \
               '`%s` *прямо сейчас* пошел _адски дристать_ лютейшей струей *поноса*'

    else:
        return

    for user in User.select():
        try:
            await config.Telegram.bot.send_message(user.uid, text % message.chat.full_name,
                                                   parse_mode='markdown')

        except Exception as e:
            logging.warning(f'Cannnot send notify to {message.chat.id} cause: {e}')
