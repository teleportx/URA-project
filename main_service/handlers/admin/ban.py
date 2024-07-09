from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject

import config
from db.User import Ban, User
from filters import CommandMention
from filters import UserAuthFilter

router = Router()


@router.message(CommandMention("ban"), UserAuthFilter(admin=True))
async def ban(message: types.Message, command: CommandObject, user: User):
    if command.args is None:
        await message.reply('Пример:\n`/ban <user_id> <reason>`')
        return

    args = command.args.split()

    if len(args) == 0:
        await message.reply('Пожалуйста укажите айди и причину бана.')
        return

    if len(args) == 1:
        await message.reply('Пожалуйста укажите причину бана.')
        return

    ban_id = args[0]

    if not ban_id.isnumeric():
        await message.reply('Айди должно быть числом.')
        return

    ban_id = int(ban_id)
    reason = ' '.join(args[1:])

    if await Ban.filter(uid=ban_id).exists():
        await message.reply('Пользователь уже забанен.')
        return

    admin_user = await User.filter(uid=ban_id, admin=True).get_or_none()
    if admin_user is not None:
        await message.reply('Админа можно забанить только через базу данных. Сообщаем всем.')

        text = (f'❗️ Админ *{user.name}* _({user.uid})_ хочет забанить админа *{admin_user.name}* _({admin_user.uid})_\n'
                f'```Причина:\n{reason}```')

        async for send_to in User.filter(admin=True):
            await config.bot.send_message(send_to.uid, text)

        return

    await Ban.create(uid=ban_id, reason=reason, banned_by=user.uid)
    await message.reply(f'Пользователь `{ban_id}` забанен по причине `{reason}`')

    try:
        text = ('*Вы забанены в боте!* Ваши действия теперь игнорируются и не будут обрабатываться.\n'
                'Если вы считаете, что произошла ошибка обратитесь к администрации.\n'
                'https://www.youtube.com/watch?v=XeoS-zsGVCs')
        await config.bot.send_message(ban_id, text)

    except:
        ...


@router.message(Command("unban"), UserAuthFilter(admin=True))
async def unban(message: types.Message, command: CommandObject):
    if command.args is None:
        await message.reply('Пример:\n`/unban <user_id>`')
        return

    if not command.args.isnumeric():
        await message.reply('Айди должно быть числом.')
        return

    ban_id = int(command.args)

    ban = await Ban.filter(uid=ban_id).get_or_none()
    if ban is None:
        await message.reply('Такой пользователь не забанен.')
        return

    await ban.delete()
    await message.reply(f'Пользователь `{ban_id}` разбанен.')

    try:
        await config.bot.send_message(ban_id, 'Вы разбанены в боте.')

    except:
        ...
