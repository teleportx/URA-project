from aiogram import Router, F, types
from aiogram.filters import Command, MagicData, CommandObject

import config
from db.User import User
from db.UserUnion import FriendRequest
from keyboards.friend import request_friend_keyboard
from keyboards.friend.request_friend_keyboard import ActionRequestUserCallback

router = Router()


@router.message(Command("start"), MagicData(F.command.args.startswith('IF')))
async def send_request(message: types.Message, command: CommandObject, user: User):
    user_id = str(command.args).replace('IF', '')
    if not user_id.isnumeric():
        return
    user_id = int(user_id)

    if user_id == user.uid:
        await message.reply('Вы не можете подать заявку самому себе.')
        return

    request_user = await User.filter(pk=user_id).get_or_none()
    if request_user is None:
        await message.reply('Пользователь не найден.')
        return

    if await FriendRequest.filter(user=user, requested_user=request_user).exists():
        await message.reply('Вы уже подавали заявку этому пользователю.')
        return

    if await request_user.friends.filter(uid=user.uid).exists():
        await message.reply('Вы уже друзья.')
        return

    # contr request
    contr_request = await FriendRequest.filter(user=request_user, requested_user=user).get_or_none()
    if contr_request is not None:
        if contr_request.message_id is not None:
            await config.bot.delete_message(user.uid, contr_request.message_id)

        await contr_request.delete()
        await user.friends.add(request_user)
        await request_user.friends.add(user)

        await config.bot.send_message(request_user.uid, f'_{user.name}_ добавил вас в друзья!')
        await message.answer(f'Вы добавили в друзья _{request_user.name}_.')
        return

    message_id = None
    if not request_user.mute_friend_requests:
        message_id = ((await config.bot.send_message(user_id, f'_{user.name}_ хочет добавить вас в друзья.',
                                                     reply_markup=request_friend_keyboard.get(user.uid, user_id)))
                      .message_id)

    await FriendRequest.create(user=user, requested_user=request_user, message_id=message_id)

    await message.reply(f'Успешно отправили запрос на добавление в друзья пользователя _{request_user.name}_')


@router.callback_query(ActionRequestUserCallback.filter())
async def action_request(callback: types.CallbackQuery, user: User):
    cb_data = ActionRequestUserCallback.unpack(callback.data)
    user_sender = await User.filter(pk=cb_data.uid).get()

    not_admin = not user.admin and not user_sender.admin
    if cb_data.result:
        if await user.friends.all().count() >= config.Constants.friends_limit and not_admin:
            await callback.answer('У вас максимальное количество друзей.')
            return

        if await user_sender.friends.all().count() >= config.Constants.friends_limit and not_admin:
            await callback.answer('У пользователя, который отправил заявку, максимальное количество друзей.')

            await FriendRequest.filter(user=user_sender, requested_user=user).delete()
            await callback.message.delete()
            return

    await FriendRequest.filter(user=user_sender, requested_user=user).delete()
    await callback.message.edit_text(callback.message.text + f'\n\n*{["ОТКЛОНЕНА", "ОДОБРЕНА"][cb_data.result]}*')

    if cb_data.result:
        await user.friends.add(user_sender)
        await user_sender.friends.add(user)

        await config.bot.send_message(user_sender.uid, f'_{user.name}_ добавил вас в друзья!')
