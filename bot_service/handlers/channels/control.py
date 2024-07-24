import aiogram
import tortoise
from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
from db import UserUnion
from db.User import User
from db.UserUnion import Channel
from keyboards.channel import channels_keyboard
from keyboards.channel.channels_keyboard import ChannelCallback, ChannelPagedCallback
from middlewares.channel import ChannelMiddleware

router = Router()


class CreateChannelStates(StatesGroup):
    send_message_from_channel = State()


channel_menu_text = 'Каналы'

router.callback_query.middleware.register(ChannelMiddleware(channel_menu_text))


@router.message(Command('channels'))
async def channels_menu(message: types.Message, user: User):
    await message.answer(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, 0))


@router.callback_query(ChannelPagedCallback.filter(F.unit == "menu"))
async def channels_menu_callback(callback: types.CallbackQuery, user: User):
    data = ChannelPagedCallback.unpack(callback.data)
    await callback.message.edit_text(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, data.page))


@router.callback_query(ChannelCallback.filter(F.action == 'create'))
async def create_channel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f'Для начала добавьте бота @{config.bot_me.username} в ваш канал.\n'
                                     f'Затем перешлите <b>любое</b> сообщение из этого канала сюда.\n\n'
                                     f'Для отмены пропишите /cancel')

    await state.set_state(CreateChannelStates.send_message_from_channel)
    await state.update_data(last_msg=callback.message.message_id)


@router.message(CreateChannelStates.send_message_from_channel, F.forward_from_chat)
async def create_channel_message_from(message: types.Message, user: User, state: FSMContext):
    await message.delete()
    last_msg = (await state.get_data()).get('last_msg')

    channel_id = message.forward_from_chat.id
    try:
        channel = await message.bot.get_chat(channel_id)

    except aiogram.exceptions.TelegramForbiddenError:
        await message.bot.edit_message_text('Бот не состоит в этом канале.\n\n'
                                            'Для отмены пропишите /cancel', message.chat.id, last_msg)
        return

    if channel.type != 'channel':
        await message.bot.edit_message_text('Вы должны переслать сообщение именно из канала.\n\n'
                                            'Для отмены пропишите /cancel', message.chat.id, last_msg)
        return

    try:
        channel_instance = await Channel.create(channel_id=channel_id, name=channel.full_name)

    except tortoise.exceptions.IntegrityError as err:
        if not err.args[0].startswith('duplicate'):
            raise err
        await message.bot.edit_message_text('Этот канал уже добавлен в бота.\n\n'
                                            'Для отмены пропишите /cancel', message.chat.id, last_msg)
        return

    await channel_instance.members.add(user)

    await state.clear()
    await message.bot.edit_message_text('Канал успешно создан!', message.chat.id, last_msg,
                                        reply_markup=await channels_keyboard.get_menu(user, 0))


@router.callback_query(ChannelCallback.filter(F.action == 'channel'))
async def show_channel(callback: types.CallbackQuery, user: User, channel: Channel):
    try:
        channel_bot = await callback.bot.get_chat(channel.channel_id)

    except aiogram.exceptions.TelegramForbiddenError:
        await callback.message.edit_text(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, 0))
        await callback.answer('Бот больше не в канале.', show_alert=True)
        return

    # Update channel name if changed
    if channel.name != channel_bot.full_name:
        channel.name = channel_bot.full_name
        await channel.save()
        await callback.answer('У канала обновлено имя.')

    channel_admins = await channel_bot.get_administrators()
    is_owner = False
    for el in channel_admins:
        if el.user.id == user.uid:
            is_owner = True
            break

    invite_link = f'https://t.me/{config.bot_me.username}?start=IC{channel.pk}P{channel.password}'
    text = (f'Канал <b>{channel.name}</b> (<code>{channel.pk}</code>)\n'
            f'Человек <b>{await channel.members.all().count()}</b>\n'
            f'Пердежы: <b>{["Выключены", "Включены"][channel.notify_perdish]}</b>\n\n'
            f'<i>Создан {channel.created_at}</i>\n\n'
            f'Ссылка-приглашение:\n<code>{invite_link}</code>')

    if not is_owner:
        text = '\n'.join(text.splitlines()[:3])

    await callback.message.edit_text(text, reply_markup=channels_keyboard.get_channel(channel.channel_id, is_owner))


@router.callback_query(ChannelCallback.filter(F.action == 'password'))
async def change_channel_password(callback: types.CallbackQuery, user: User, channel: Channel):
    channel.password = UserUnion.generate_password()
    await channel.save()
    await callback.answer('Пароль канала изменен.')
    await show_channel(callback, user, channel)


@router.callback_query(ChannelCallback.filter(F.action == 'perdish'))
async def change_channel_perdish(callback: types.CallbackQuery, user: User, channel: Channel):
    channel.notify_perdish = not channel.notify_perdish
    await channel.save()
    await callback.answer('Пердежи канала изменены.')
    await show_channel(callback, user, channel)
