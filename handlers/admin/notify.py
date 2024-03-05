import asyncio
import logging

from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from tortoise.functions import Count

import config
from db.User import User, Notify
from filters.user import UserAuthFilter
from keyboards import notify_keyboard

router = Router()


class SendNotify(StatesGroup):
    writing_message = State()
    submit = State()


@router.message(Command("notify"), UserAuthFilter(admin=True))
async def notify(message: types.Message, state: FSMContext):
    text = (f'Отправьте текст, который хотите отправить в качестве уведомления.\n\n'
            f'*Правила форматирования:*\n\n'
            f'-\*- - code style (like \`\`\`)\n'
            f'```Header\n'
            f'text```\n\n'
            f''
            f'\`\` - copyable\n'
            f'`text`\n\n'
            f''
            f'\_ - cursive\n'
            f'_text_\n\n'
            f''
            f'\* - bold\n'
            f'*text*\n\n')

    await message.delete()

    await state.set_state(SendNotify.writing_message)
    last_msg = await message.answer(text, reply_markup=notify_keyboard.get(only_cancel=True))
    await state.update_data({'last_msg': last_msg.message_id})


@router.message(SendNotify.writing_message)
async def notify_get_message(message: types.Message, state: FSMContext):
    last_msg = (await state.get_data()).get('last_msg')

    text = (message.text
            .replace('``', '`')
            .replace('-*-', '```'))
    await state.update_data({'text': text})
    await state.set_state(SendNotify.submit)

    await message.delete()
    await config.Telegram.bot.edit_message_text(
        f'Предпросмотр отправляемого сообщения:\n{text}\n\nПодтверждаем отправку?',
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
    text = (await state.get_data()).get('text')

    users = await User.all()
    notify_instance = await Notify.create(text=text, initiated_by=user, init_queue_size=len(users))
    await notify_instance.queue.add(*users)

    admin_text = (f'Отправка уведомлений начата.\n'
                  f'Айди уведомления `{notify_instance.pk}`\n'
                  f'Получить актуальную информацию о рассылке: `/nstatus {notify_instance.pk}`')
    await callback.message.edit_text(admin_text)

    await state.clear()


@router.message(Command("nstatus"), UserAuthFilter(admin=True))
async def notify(message: types.Message, command : CommandObject):
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

    notify_instance = await Notify.filter(id=notify_id).get_or_none()
    if notify_instance is None:
        await message.reply('Уведомление не найдено.')
        return

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

    await message.reply(text)
