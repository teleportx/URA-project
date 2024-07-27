from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, MagicData, CommandObject

from db.ToiletSessions import SretSession, SretType
from db.User import User
from bot_service.filters import UserAuthFilter
from keyboards import whois_keyboard

router = Router()


async def whois_ans(message: types.Message, user_id: int):
    user = await User.all().filter(uid=user_id).get_or_none()
    if user is None:
        await message.reply(f'Пользователь с айди <code>{user_id}</code> не найден.')
        return

    last_session_timestamp = await SretSession.all().filter(user=user).order_by('-end').first()
    if last_session_timestamp is not None:
        if last_session_timestamp.end is None:
            last_session_timestamp = last_session_timestamp.start
        else:
            last_session_timestamp = last_session_timestamp.end

    perdezhs = await SretSession.all().filter(user=user, sret_type=SretType.PERNUL).count()
    toilets = await SretSession.all().filter(user=user, sret_type__in=[SretType.SRET, SretType.DRISHET]).count()

    text = (f'Пользователь <b>{user.name}</b> (<code>{user_id}</code>)\n\n'
            f'Админ: <code>{user.admin}</code>\n'
            f'Аккаунт создан: <code>{user.created_at}</code>\n'
            f'Последняя активность: <code>{last_session_timestamp}</code>\n'
            f'Всего ходил раз в туалет: <code>{toilets}</code>\n'
            f'Всего пернул: <code>{perdezhs}</code>\n\n'
            f'Написать через бота: <code>/send {user_id}</code>\n'
            f'Забанить: <code>/ban {user_id}</code>')

    await message.reply(text, reply_markup=whois_keyboard.get(user_id))


async def name_to_id(message: types.Message, user_name: str):
    user = await User.all().filter(name=user_name).get_or_none()
    if user is None:
        await message.reply(f'Пользователь с именем <code>{user_name}</code> не найден.')
        return

    await whois_ans(message, user.uid)


@router.message(Command("whois"), UserAuthFilter(admin=True), MagicData(~F.command.args))
async def whois_by_message(message: types.Message):
    if message.reply_to_message is None:
        await message.reply('Вы должны ссылаться на сообщение с уведомлением для получения информации.')
        return

    if 'ВНИМАНИЕ' not in message.reply_to_message.text:
        await message.reply('К сожалению мы не может получить информацию о пользователе из этого сообщения.')
        return

    text = message.reply_to_message.html_text
    i = text.find('<code>') + 6
    j = text.find('</code>')

    name = text[i:j]
    await name_to_id(message, name)


@router.message(Command("whois"), UserAuthFilter(admin=True), MagicData(F.command.args.isnumeric()))
async def whois_by_id(message: types.Message, command: CommandObject):
    await whois_ans(message, int(command.args))


@router.message(Command("whois"), UserAuthFilter(admin=True), MagicData(~F.command.args.isnumeric()))
async def whois_by_name(message: types.Message, command: CommandObject):
    await name_to_id(message, command.args)
