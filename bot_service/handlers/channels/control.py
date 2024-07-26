from typing import Tuple, List

import aiogram
import tortoise
from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
from db import UserUnion
from db.User import User
from db.UserUnion import Channel
from keyboards.channel import channels_keyboard
from keyboards.channel.channels_keyboard import ChannelCallbackData, ChannelPagedCallbackData, \
    ChannelMemberDeleteCallbackData
from middlewares.channel import ChannelMiddleware
from utils.find_button_by_callback import find_button_by_callback_data

router = Router()


class CreateChannelStates(StatesGroup):
    send_message_from_channel = State()


channel_menu_text = ('<b>Меню управления каналами.</b>\n'
                     'Присоединяйтесь в каналы, чтобы уведомлять большое число людей, когда вы идете срать! '
                     'В канале уведомление о том, что вы идете срать придет в созданный вами тг канал.\n\n'
                     'Добавляйте в тг канал кого хотите, а в канал ура, только тех кто будет уведомлять о том, что он пошел срать.')
channel_members_menu_text = 'Нажмите на пользователя, которого хотите удалить.'

router.callback_query.middleware.register(ChannelMiddleware(channel_menu_text))


async def get_bot_channel(bot: Bot, channel_id: int) -> Tuple[types.Chat, List[types.ChatMember]]:
    try:
        channel_bot = await bot.get_chat(channel_id)
        return channel_bot, await channel_bot.get_administrators()

    except (aiogram.exceptions.TelegramForbiddenError, aiogram.exceptions.TelegramBadRequest):

        await Channel.filter(pk=channel_id).delete()

        return None, None


async def answer_channel_deleted(callback: types.CallbackQuery, user: User):
    await callback.message.edit_text(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, 0))
    await callback.answer('Бот больше не в канале.', show_alert=True)


async def is_admin_channel(channel_bot: types.Chat, user_id: int,
                           channel_admins: List[types.ChatMember] = None) -> bool:
    if channel_admins is None:
        channel_admins = await channel_bot.get_administrators()
    for el in channel_admins:
        if el.user.id == user_id:
            return True

    return False


# CHANNELS MENU
@router.message(Command('channels'))
async def channels_menu(message: types.Message, user: User):
    await message.answer(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, 0))


@router.callback_query(ChannelPagedCallbackData.filter(F.unit == "menu"))
async def channels_menu_callback(callback: types.CallbackQuery, user: User):
    data = ChannelPagedCallbackData.unpack(callback.data)
    await callback.message.edit_text(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, data.page))


# CREATING CHANNEL
@router.callback_query(ChannelCallbackData.filter(F.action == 'create'))
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


# CONTROL CHANNEL
@router.callback_query(ChannelCallbackData.filter(F.action == 'channel'))
async def show_channel(callback: types.CallbackQuery, user: User, channel: Channel):
    channel_bot, channel_admins = await get_bot_channel(callback.bot, channel.channel_id)
    if channel_bot is None:
        await answer_channel_deleted(callback, user)
        return

    # Update channel name if changed
    if channel.name != channel_bot.full_name:
        channel.name = channel_bot.full_name
        await channel.save()
        await callback.answer('У канала обновлено имя.')

    invite_link = f'https://t.me/{config.bot_me.username}?start=IC{channel.pk}P{channel.password}'
    text = (f'Канал <b>{channel.name}</b> (<code>{channel.pk}</code>)\n'
            f'Человек <b>{await channel.members.all().count()}</b>\n'
            f'Пердежы: <b>{["Выключены", "Включены"][channel.notify_perdish]}</b>\n\n'
            f'<i>Создан {channel.created_at}</i>\n\n'
            f'Ссылка-приглашение:\n<code>{invite_link}</code>')

    is_admin = await is_admin_channel(channel_bot, user.uid, channel_admins)
    if not is_admin:
        text = '\n'.join(text.splitlines()[:3])

    await callback.message.edit_text(text, reply_markup=channels_keyboard.get_channel(channel.channel_id, is_admin))


@router.callback_query(ChannelCallbackData.filter(F.action == 'leave'))
async def leave_from_channel(callback: types.CallbackQuery, user: User, channel: Channel):
    channel_bot, channel_admins = await get_bot_channel(callback.bot, channel.channel_id)
    if channel_bot is None:
        await answer_channel_deleted(callback, user)
        return
    is_admin = await is_admin_channel(channel_bot, user.uid, channel_admins)
    if is_admin:
        await callback.answer('Вы не можете ливнуть из этого канала, тк вы админ.', show_alert=True)

    await channel.members.remove(user)
    await callback.message.edit_text(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, 0))


@router.callback_query(ChannelCallbackData.filter(F.action == 'password'))
async def change_channel_password(callback: types.CallbackQuery, user: User, channel: Channel):
    channel.password = UserUnion.generate_password()
    await channel.save()
    await callback.answer('Пароль канала изменен.')
    await show_channel(callback, user, channel)


@router.callback_query(ChannelCallbackData.filter(F.action == 'perdish'))
async def change_channel_perdish(callback: types.CallbackQuery, user: User, channel: Channel):
    channel.notify_perdish = not channel.notify_perdish
    await channel.save()
    await callback.answer('Пердежи канала изменены.')
    await show_channel(callback, user, channel)


@router.callback_query(ChannelPagedCallbackData.filter(F.unit == 'members'))
async def show_channel_members(callback: types.CallbackQuery, channel: Channel):
    cb_data = ChannelPagedCallbackData.unpack(callback.data)
    await callback.message.edit_text(channel_members_menu_text,
                                     reply_markup=await channels_keyboard.get_channel_members(channel, cb_data.page))


@router.callback_query(ChannelMemberDeleteCallbackData.filter(~F.submit))
async def delete_channel_member(callback: types.CallbackQuery):
    clicked_button = find_button_by_callback_data(callback.message.reply_markup, callback.data)
    cb_data = ChannelMemberDeleteCallbackData.unpack(callback.data)

    await callback.message.edit_text(
        f'Вы уверены, что хотите удалить из канала пользователя <b>{clicked_button.text}</b>?',
        reply_markup=channels_keyboard.get_delete_user_submit(cb_data.channel_id, cb_data.user_id))


@router.callback_query(ChannelMemberDeleteCallbackData.filter(F.submit))
async def delete_channel_member_submit(callback: types.CallbackQuery, user: User, channel: Channel):
    channel_bot, channel_admins = await get_bot_channel(callback.bot, channel.channel_id)
    if channel_bot is None:
        await answer_channel_deleted(callback, user)
        return

    cb_data = ChannelMemberDeleteCallbackData.unpack(callback.data)

    if await is_admin_channel(channel_bot, cb_data.user_id, channel_admins):
        await callback.answer('Вы не можете удалить админа из канала.', show_alert=True)

    else:
        # GoVnOcOdE
        delete_user = await User.get(pk=cb_data.user_id)
        await channel.members.remove(delete_user)

        await callback.bot.send_message(cb_data.user_id, f'Вы исключены из канала <b>{channel.name}</b>')

        await callback.answer('Пользователь удален.')

    await callback.message.edit_text(channel_members_menu_text,
                                     reply_markup=await channels_keyboard.get_channel_members(channel, 0))


@router.callback_query(ChannelCallbackData.filter(F.action == 'delete'))
async def delete_channel(callback: types.CallbackQuery, channel: Channel):
    await callback.message.edit_text(f'Вы уверены, что хотите удалить канал <b>{channel.name}</b>?',
                                     reply_markup=channels_keyboard.get_channel_delete_submit(channel.channel_id))


@router.callback_query(ChannelCallbackData.filter(F.action == 'delete_submit'))
async def delete_channel_submit(callback: types.CallbackQuery, user: User, channel: Channel):
    await channel.delete()
    await callback.answer('Канал удален.')
    await callback.message.edit_text(channel_menu_text, reply_markup=await channels_keyboard.get_menu(user, 0))
