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

router = Router()


async def verify_action(user: User, sret: int, message: Optional[types.Message] = None):
    last_session = await SretSession.filter(user=user).order_by('-message_id').first()

    has_opened_session = False
    if last_session is not None:
        has_opened_session = last_session.end is None

    if sret in send_srat_notification.must_sret and not has_opened_session:
        if message is not None:
            await message.reply('Ты что заканчивать захотел? Ты даже не срешь!')
        return False

    if sret in send_srat_notification.must_not_sret and has_opened_session:
        if message is not None:
            await message.reply('Ты прошлое свое сранье не закончил, а уже новое начинаешь?\n'
                                'Нет уж. Будь добр, раз начал - закончи.')
        return False

    if has_opened_session or last_session is None:
        return True

    throttling_time = timedelta(minutes=config.Constants.throttling_time_actions[last_session.sret_type - 1][sret - 1])
    now = datetime.now(pytz.UTC).astimezone()
    if (now - last_session.end) <= throttling_time:
        if message is not None:
            wait_time = round((throttling_time - (now - last_session.end)).total_seconds())
            await message.reply(f'Вы совершаете действия слишком часто!\n'
                                f'Подождите еще *{wait_time} секунд*')
        return False

    return True


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
