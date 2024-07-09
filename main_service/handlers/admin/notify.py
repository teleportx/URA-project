import asyncio

import aiogram
from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from tortoise.functions import Count

import config
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
    notify_instance = await Notify.create(message_id=original_message_id, initiated_by=user, init_queue_size=len(users))
    await notify_instance.queue.add(*users)

    admin_text = (f'Отправка уведомлений начата.\n'
                  f'Айди уведомления `{notify_instance.pk}`\n'
                  f'Получить актуальную информацию о рассылке:\n`/nstatus {notify_instance.pk}`')
    await callback.message.edit_text(admin_text)

    await state.clear()


async def get_notify_status_text(notify_id: int) -> str:
    notify_instance = await Notify.filter(pk=notify_id).get_or_none()
    if notify_instance is None:
        return ''

    queue_size = await notify_instance.queue.all().count()
    if queue_size == 0:
        status = 'ЗАВЕРШЕНО'

    elif queue_size == notify_instance.init_queue_size:
        status = 'В ОЧЕРЕДИ'

    else:
        status = 'В ПРОЦЕССЕ'

    percent = round(((notify_instance.init_queue_size - queue_size) / notify_instance.init_queue_size) * 100, 1)
    text = (f'Уведомление *№{notify_id}*\n'
            f'Статус: *{status}*\n\n'
            f'Отправлено: {notify_instance.init_queue_size - queue_size}/{notify_instance.init_queue_size} - {percent}%\n'
            f'Ошибок: {notify_instance.errors}')

    if queue_size != 0:
        text += f'\n\n_Время рассылки ~{round(queue_size * 2 / 60, 1)} мин_'

    return text


@router.message(Command("nstatus"), UserAuthFilter(admin=True))
async def nstatus(message: types.Message, command: CommandObject):
    if command.args is None:
        text = '*Очередь уведомлений:*\n'

        notifys = Notify.annotate(queue_count=Count('queue')).filter(queue_count__not=0).order_by('created_at').limit(5)
        async for notify_o in notifys:
            ost_size = notify_o.init_queue_size - await notify_o.queue.all().count()

            now = f'{ost_size}/{notify_o.init_queue_size}' if ost_size != 0 else 'в очереди'
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
