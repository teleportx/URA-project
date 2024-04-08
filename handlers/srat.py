from typing import Optional

from aiogram import types, Router, F
from aiogram.enums import ChatType
from aiogram.types import InlineQueryResultArticle, InlineQuery, InputTextMessageContent, ChosenInlineResult

import config
from db.ToiletSessions import SretSession
from db.User import User
from keyboards.srat_var_keyboard import SretActions
from utils import send_srat_notification

router = Router()


async def verify_action(user: User, sret: int, message: Optional[types.Message] = None):
    if sret in send_srat_notification.must_sret:
        if not await SretSession.filter(user=user, end=None).exists():
            if message is not None:
                await message.reply('Ты что заканчивать захотел? Ты даже не срешь!')
            return False

    if sret in send_srat_notification.must_not_sret:
        if await SretSession.filter(user=user, end=None).exists():
            if message is not None:
                await message.reply('Ты прошлое свое сранье не закончил, а уже новое начинаешь?\n'
                                    'Нет уж. Будь добр, раз начал - закончи.')
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


@router.callback_query(F.data == 'cancel_srat')
async def cancel_srat(callback: types.CallbackQuery):
    await SretSession.filter(message_id=callback.message.message_id).update(autoend=False)

    await callback.answer('Отменили автозавершение.')
    await callback.message.edit_reply_markup()


@router.inline_query()
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
