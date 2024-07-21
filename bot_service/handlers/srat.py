from datetime import datetime, timedelta
from typing import Optional

import pytz
from aiogram import types, Router, F
from aiogram.enums import ChatType
from aiogram.types import InlineQueryResultArticle, InlineQuery, InputTextMessageContent, ChosenInlineResult
from tortoise import Tortoise

import config
from db.ToiletSessions import SretSession
from db.User import User
from keyboards import sret_keyboard
from keyboards.srat_var_keyboard import SretActions
from utils import send_srat_notification
from utils.send_srat_notification import verify_action

router = Router()


@router.message(F.text.startswith('Я'), F.chat.type == ChatType.PRIVATE)
async def send_srat(message: types.Message, user: User):
    sret = None
    for el in SretActions:
        if el.value[1] == message.text:
            sret = el.value[0]
            break
    if sret is None:
        return

    if not await verify_action(user, sret, message):
        return

    await message.delete()
    await send_srat_notification.send(user, sret)


@router.callback_query(F.data == 'chg_aend_srat')
async def cancel_srat(callback: types.CallbackQuery):
    dbconn = Tortoise.get_connection('default')
    query = (f'UPDATE {config.DB.db_name}.public.sretsession SET autoend = NOT autoend '
             f'WHERE message_id = {callback.message.message_id} '
             f'RETURNING autoend;')
    now_autoend = (await dbconn.execute_query_dict(query))[0].get('autoend')

    await callback.answer(f'{["Выключили", "Включили"][now_autoend]} автозавершение.')
    await callback.message.edit_reply_markup(reply_markup=sret_keyboard.get(now_autoend))


@router.inline_query(F.query == '')
async def get_sret_actions(inline_query: InlineQuery, user: User):
    res = []
    exists = await SretSession.filter(user=user, end=None).exists()
    for el in SretActions:
        sret = int(el.value[0])
        in_must = sret in send_srat_notification.must_sret
        inn_must = sret in send_srat_notification.must_not_sret
        if in_must and exists or \
                inn_must and not exists or (not in_must and not inn_must):
            res.append(InlineQueryResultArticle(
                id=str(el.value[0]),
                title=el.value[1],
                input_message_content=InputTextMessageContent(
                    message_text=send_srat_notification.get_message_text(user, el.value[0])
                )
            ))

    await inline_query.answer(res, is_personal=True, cache_time=0)


@router.chosen_inline_result()
async def send_srat_inline(chosen_result: ChosenInlineResult, user: User):
    sret = int(chosen_result.result_id)
    if not await verify_action(user, sret):
        text = 'Эй! Полегче! Вы совершили невозможное для вашей жопы действие! Вы конечно молодец, но мы не отправим уведомление об этом действии всем.'
        await config.bot.send_message(chosen_result.from_user.id, text)
        return

    smessage_id = await send_srat_notification.send(user, sret)

    if sret in send_srat_notification.must_not_sret:
        await SretSession.filter(message_id=smessage_id).update(autoend=False)
