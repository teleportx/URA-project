import asyncio

import aiogram
from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from tortoise.functions import Count

import config
from brocker import message_sender
from db.User import User, Notify
from main_service.filters import UserAuthFilter
from keyboards import notify_keyboard

router = Router()


class SendNotify(StatesGroup):
    writing_message = State()
    submit = State()


@router.message(Command("notify"), UserAuthFilter(admin=True))
async def notify(message: types.Message, state: FSMContext):
    text = (f'Отправьте текст, который хотите отправить в качестве уведомления.\n\n'
            f'*Правила форматирования:*\n_Такое же как в обычных сообщениях_')

    await message.delete()

    await state.set_state(SendNotify.writing_message)
    last_msg = await message.answer(text, reply_markup=notify_keyboard.get(only_cancel=True))
    await state.update_data({'last_msg': last_msg.message_id})


@router.message(SendNotify.writing_message)
async def notify_get_message(message: types.Message, state: FSMContext):
    last_msg = (await state.get_data()).get('last_msg')

    await state.set_state(SendNotify.submit)
    await state.update_data({'message_id': message.message_id})

    await config.bot.edit_message_text(
        f'Получили, Подтверждаем отправку?',
        message.chat.id,
        last_msg,
        reply_markup=notify_keyboard.get(),
    )


@router.callback_query(notify_keyboard.Notify.filter(F.action == 'cancel'))
async def cancel_notify(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Отменили отправку.')

    await asyncio.sleep(5)
    await callback.message.delete()


@router.callback_query(SendNotify.submit, notify_keyboard.Notify.filter(F.action == 'submit'))
async def submit_notify(callback: types.CallbackQuery, state: FSMContext, user: User):
    original_message_id = (await state.get_data()).get('message_id')

    users = await User.all()
    notify_instance = await Notify.create(message_id=original_message_id, initiated_by=user, scheduled_users_count=len(users))

    for send_to in users:
        await message_sender.send_message(send_to.uid, user.uid, original_message_id, 0, notify_instance.pk)

    admin_text = (f'Отправка уведомлений начата.\n'
                  f'Айди уведомления <code>{notify_instance.pk}</code>\n'
                  f'Получить актуальную информацию о рассылке:\n<code>/nstatus {notify_instance.pk}</code>')
    await callback.message.edit_text(admin_text)

    await state.clear()


async def get_notify_status_text(notify_id: int) -> str:
    notify_instance = await Notify.filter(pk=notify_id).get_or_none()
    if notify_instance is None:
        return ''

    if notify_instance.executed_users_count == notify_instance.scheduled_users_count:
        status = 'ЗАВЕРШЕНО'

    elif notify_instance.executed_users_count == 0:
        status = 'В ОЧЕРЕДИ'

    else:
        status = 'В ПРОЦЕССЕ'

    percent = round((notify_instance.executed_users_count / notify_instance.scheduled_users_count) * 100, 1)
    text = (f'Уведомление <b>№{notify_id}</b>\n'
            f'Статус: <b>{status}</b>\n\n'
            f'Исполнено: {notify_instance.executed_users_count}/{notify_instance.scheduled_users_count} - {percent}%')

    if notify_instance.executed_users_count != notify_instance.scheduled_users_count:
        text += f'\n\n<i>Время рассылки ~{round((notify_instance.scheduled_users_count - notify_instance.executed_users_count) * 2 / 60, 1)} мин</i>'

    return text


@router.message(Command("nstatus"), UserAuthFilter(admin=True))
async def nstatus(message: types.Message, command: CommandObject):
    if command.args is None:
        text = '<b>Очередь уведомлений:</b>\n'

        notifys = Notify.all().order_by('created_at').limit(5)
        async for notify_o in notifys:
            now = f'{notify_o.executed_users_count}/{notify_o.init_queue_size}' if notify_o.executed_users_count != 0 else 'в очереди'
            text += f'- №{notify_o.pk}: _{now}_\n'

        await message.reply(text)

        return

    if not command.args.isnumeric():
        await message.reply('Айди должно быть числом')
        return
    notify_id = int(command.args)

    text = await get_notify_status_text(notify_id)
    if text == '':
        await message.reply('Уведомление не найдено.')
        return

    await message.reply(text, reply_markup=notify_keyboard.get_update())


@router.callback_query(notify_keyboard.Notify.filter(F.action == 'update'))
async def nstatus_update(callback: types.CallbackQuery):
    i = callback.message.text.find('№')
    j = callback.message.text.find('\n')
    notify_id = callback.message.text[i + 1:j]

    if not notify_id.isnumeric():
        await callback.message.edit_text('Уведомление не найдено.')
        return

    text = await get_notify_status_text(int(notify_id))
    if text == '':
        await callback.message.edit_text('Уведомление не найдено.')
        return

    try:
        await callback.message.edit_text(text, reply_markup=notify_keyboard.get_update())

    except aiogram.exceptions.TelegramBadRequest:
        await callback.answer('Ничего не изменилось.')
