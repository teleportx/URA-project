from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, MagicData, CommandObject

from db.ToiletSessions import SretSession, SretType
from db.User import User
from filters.user import UserAuthFilter
from keyboards import whois_keyboard

router = Router()


async def whois_ans(message: types.Message, user_id: int):
    user = await User.all().filter(uid=user_id).get_or_none()
    if user is None:
        await message.reply(f'Пользователь с айди `{user_id}` не найден.')
        return

    last_session_timestamp = await SretSession.all().filter(user=user).order_by('-end').first()
    if last_session_timestamp is not None:
        if last_session_timestamp.end is None:
            last_session_timestamp = last_session_timestamp.start
        else:
            last_session_timestamp = last_session_timestamp.end

    perdezhs = await SretSession.all().filter(user=user, sret_type=SretType.PERNUL).count()
    toilets = await SretSession.all().filter(user=user, sret_type__in=[SretType.SRET, SretType.DRISHET]).count()

    text = (f'Пользователь *{user.name}* (`{user_id}`)\n\n'
            f'Админ: `{user.admin}`\n'
            f'Аккаунт создан: `{user.created_at}`\n'
            f'Последняя активность: `{last_session_timestamp}`\n'
            f'Всего ходил раз в туалет: `{toilets}`\n'
            f'Всего пернул: `{perdezhs}`\n\n'
            f'Написать через бота: `/send {user_id}`\n'
            f'Забанить: `/ban {user_id}`')

    await message.reply(text, reply_markup=whois_keyboard.get(user_id))


async def name_to_id(message: types.Message, user_name: str):
    user = await User.all().filter(name=user_name).get_or_none()
    if user is None:
        await message.reply(f'Пользователь с именем `{user_name}` не найден.')
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

    text = message.reply_to_message.md_text
    i = text.find('`') + 1
    j = text.find('`', i)

    name = text[i:j]
    await name_to_id(message, name)


@router.message(Command("whois"), UserAuthFilter(admin=True), MagicData(F.command.args.isnumeric()))
async def whois_by_id(message: types.Message, command: CommandObject):
    await whois_ans(message, int(command.args))


@router.message(Command("whois"), UserAuthFilter(admin=True), MagicData(~F.command.args.isnumeric()))
async def whois_by_name(message: types.Message, command: CommandObject):
    await name_to_id(message, command.args)
