from aiogram import Router, F
from aiogram import types
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandObject, MagicData
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, CREATOR, ADMINISTRATOR
from db.User import User
from db.UserUnion import Channel
from handlers.channels.control import get_bot_channel

router = Router()


@router.message(Command("start"), MagicData(F.command.args.startswith('IC')))
async def join_channel(message: types.Message, command: CommandObject, user: User):
    try:
        channel_id, channel_password = command.args[2:].split('P')[:2]

    except ValueError:
        return

    if not channel_id[1:].isnumeric() and not channel_id[0].isnumeric() and channel_id[0] != '-':
        await message.reply('Канал не найден.')
        return

    channel_id = int(channel_id)

    channel = await Channel.filter(pk=channel_id, password=channel_password).get_or_none()
    if channel is None:
        await message.reply('Канал не найден.')
        return

    channel_bot = (await get_bot_channel(message.bot, channel_id))[0]
    if channel_bot is None:
        await message.reply('Канал не найден.')
        return

    member = await channel_bot.get_member(user.uid)

    if member.status in [ChatMemberStatus.KICKED, ChatMemberStatus.LEFT]:
        await message.reply('Вас нет в тг канале, вы не можете вступать в этот канал.')
        return

    if await channel.members.filter(uid=user.uid).exists():
        await message.reply('Вы уже состоите в этом канале.')
        return

    await channel.members.add(user)
    await message.reply(f'Добро пожаловать в канал <b>{channel.name}</b>!')


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT) << (MEMBER | CREATOR | ADMINISTRATOR)))
async def kick_from_channel(update: types.ChatMemberUpdated, user: User):
    channel = await Channel.get_or_none(pk=update.chat.id)
    if channel is None:
        return

    await update.bot.send_message(user.uid, f'Вы исключены из канала <b>{channel.name}</b>')
    await channel.members.remove(user)
