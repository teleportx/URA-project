from aiogram import types, Router, F
from aiogram.enums import ChatType

from db.ToiletSessions import SretSession
from db.User import User
from filters.user import UserAuthFilter
from keyboards.srat_var_keyboard import SretActions
from utils import send_srat_notification

router = Router()


@router.message(F.text.startswith('Я'), UserAuthFilter(), F.chat.type == ChatType.PRIVATE)
async def send_srat(message: types.Message, user: User):
    if message.text == SretActions.SRET.value:
        sret = 1

    elif message.text == SretActions.END.value:
        sret = 0

    elif message.text == SretActions.PERNUL.value:
        sret = 3

    elif message.text == SretActions.DRISHET.value:
        sret = 2

    else:
        return

    if sret in send_srat_notification.must_sret:
        if not await SretSession.filter(user=user, end=None).exists():
            await message.reply('Ты что заканчивать захотел? Ты даже не срешь!')
            return

    if sret in send_srat_notification.must_not_sret:
        if await SretSession.filter(user=user, end=None).exists():
            await message.reply('Ты прошлое свое сранье не закончил, а уже новое начинаешь?\n'
                                'Нет уж. Будь добр, раз начал - закончи.')
            return

    await message.delete()
    await send_srat_notification.send(user, sret)


@router.callback_query(F.data == 'cancel_srat')
async def cancel_srat(callback: types.CallbackQuery):
    await SretSession.filter(message_id=callback.message.message_id).update(autoend=False)

    await callback.answer('Отменили автозавершение.')
    await callback.message.edit_reply_markup()
