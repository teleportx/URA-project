from aiogram import Router, types, F
from aiogram.filters import Command

import config
from db.User import User
from db.UserUnion import FriendRequest
from keyboards.friend import friends_keyboard
from keyboards.friend.friends_keyboard import FriendMenuCallback, FriendUserCallback

router = Router()


def get_main_menu_text(user: User) -> str:
    friend_link = f'https://t.me/{config.bot_me.username}?start=IF{user.uid}'
    text = (f'Список ваших друзей. Для удаления нажмите на никнейм того, кого хотите удалить.\n'
            f'Если вы мутите входящие заявки в друзья, то для добавления в друзья вам нужно будет отправить ответную заявку.\n\n'
            f'Ваша ссылка для добавления вас в друзья - <code>{friend_link}</code>')

    return text


@router.message(Command('friends'))
async def friends_menu(message: types.Message, user: User):
    await message.answer(get_main_menu_text(user), reply_markup=await friends_keyboard.get(user))


@router.callback_query(FriendMenuCallback.filter(F.unit == 'main'))
async def friends_menu_callback(callback: types.CallbackQuery, user: User):
    await callback.message.edit_text(get_main_menu_text(user), reply_markup=await friends_keyboard.get(user))


@router.callback_query(FriendMenuCallback.filter(F.unit == 'chgmut'))
async def change_mute(callback: types.CallbackQuery, user: User):
    user.mute_friend_requests = not user.mute_friend_requests
    await user.save()

    await friends_menu_callback(callback, user)


@router.callback_query(FriendUserCallback.filter(F.type == friends_keyboard.FriendUserType.friend))
async def delete_friend(callback: types.CallbackQuery):
    cb_data = FriendUserCallback.unpack(callback.data)
    user_2 = await User.filter(pk=cb_data.user_id).only('name').get()

    await callback.message.edit_text(f'Вы уверены, что хотите удалить <i>{user_2.name}</i> из друзей?',
                                     reply_markup=friends_keyboard.get_submit_delete(cb_data.user_id, 'main', friends_keyboard.FriendUserType.friend_submit))


@router.callback_query(FriendUserCallback.filter(F.type == friends_keyboard.FriendUserType.friend_submit))
async def delete_friend_submit(callback: types.CallbackQuery, user: User):
    cb_data = FriendUserCallback.unpack(callback.data)
    user_2 = await User.filter(pk=cb_data.user_id).get()

    await user.friends.remove(user_2)
    await user_2.friends.remove(user)

    await callback.answer(f'Удалили {user_2.name} из друзей.')
    await friends_menu_callback(callback, user)


@router.callback_query(FriendMenuCallback.filter(F.unit == 'req'))
async def friend_requests_menu(callback: types.CallbackQuery, user: User):
    await callback.message.edit_text('Ваши заявки в друзья. Для удаления нажмите на никнейм того, кого хотите удалить.',
                                     reply_markup=await friends_keyboard.get_requests(user))


@router.callback_query(FriendUserCallback.filter(F.type == friends_keyboard.FriendUserType.request))
async def delete_friend_request(callback: types.CallbackQuery):
    cb_data = FriendUserCallback.unpack(callback.data)
    user_2 = await User.filter(pk=cb_data.user_id).only('name').get()

    await callback.message.edit_text(f'Вы уверены, что хотите отозвать заявку <i>{user_2.name}</i> в друзья?',
                                     reply_markup=friends_keyboard.get_submit_delete(cb_data.user_id, 'req', friends_keyboard.FriendUserType.request_submit))


@router.callback_query(FriendUserCallback.filter(F.type == friends_keyboard.FriendUserType.request_submit))
async def delete_friend_request_submit(callback: types.CallbackQuery, user: User):
    cb_data = FriendUserCallback.unpack(callback.data)
    user_2 = await User.filter(pk=cb_data.user_id).get()

    # govnocode request
    request = await FriendRequest.filter(user=user, requested_user=user_2).get()
    await request.delete()

    if request.message_id is not None:
        try:
            await config.bot.delete_message(user_2.uid, request.message_id)

        except:
            await config.bot.edit_message_text('<i>Удаленная заявка</i>', reply_markup=None)

    await callback.answer(f'Отозвали заявку {user_2.name} в друзья.')
    await friend_requests_menu(callback, user)
