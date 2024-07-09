import asyncio

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import config
from db.User import User
from db.UserUnion import Group
from keyboards.group import groups_keyboard
from middlewares.group import GroupMiddleware
from utils.verify_name import verify_name

router = Router()
router.callback_query.middleware.register(GroupMiddleware())


class NamingGroupStates(StatesGroup):
    writing_name = State()


class DeleteGroupStates(StatesGroup):
    writing_name = State()


# GROUP MAIN MENU
@router.message(Command('groups'))
async def groups_menu(message: types.Message, user: User):
    await message.answer('Выберите группу.', reply_markup=await groups_keyboard.get_all(user))


@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'main'))
async def groups_menu_callback(callback: types.CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Выберите группу.', reply_markup=await groups_keyboard.get_all(user))


# CREATE GROUP
@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'create'))
async def create_group(callback: types.CallbackQuery, state: FSMContext, user: User):
    if not user.admin and await user.groups_member.all().count() >= config.Constants.member_group_limit:
        await callback.answer(f'Вы не можете состоять более чем в {config.Constants.member_group_limit} группах.', show_alert=True)
        return

    await callback.message.edit_text(
        'Напишите название для вашей группы. Оно должно быть не длиннее 32 символов и не содержать специальных символов.')

    await state.set_state(NamingGroupStates.writing_name)
    await state.update_data({'last_msg': callback.message.message_id})


@router.message(NamingGroupStates.writing_name)
async def group_writing_name(message: types.Message, state: FSMContext, user: User):
    state_data = (await state.get_data())
    last_msg = state_data.get('last_msg')
    await message.delete()

    if len(message.text) > 32:
        await config.bot.edit_message_text('Название должно быть не длиннее 32 символов.', user.uid, last_msg)
        return

    if not verify_name(message.text.replace(' ', '')):
        await config.bot.edit_message_text('Название не должно содержать специальные символы.', user.uid, last_msg)
        return

    if state_data.get('group_id') is not None:
        group = await Group.filter(pk=state_data.get('group_id')).get()
        group.name = message.text
        await group.save()

        info_message = await message.answer('Название группы успешно изменено!')

        await state.clear()
        await show_group(None, group, user, state, last_msg, user.uid)

        await asyncio.sleep(3)
        await info_message.delete()
        return

    created_group = await Group.create(name=message.text, owner=user)
    await created_group.members.add(user)

    await config.bot.edit_message_text(f'Ваша группа `{message.text}` успешно создана!\n',
                                       user.uid, last_msg,
                                       reply_markup=groups_keyboard.get_return('Перейти к управлению группами'))

    await state.clear()


# GROUP CONTROL
@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'show'))
async def show_group(callback: types.CallbackQuery, group: Group, user: User, state: FSMContext, message_id: int = None,
                     chat_id: int = None):
    await state.clear()
    owner = await group.owner

    invite_link = f'https://t.me/{config.bot_me.username}?start=IG{group.pk}P{group.password}'
    text = (f'Группа *{group.name}* (`{group.pk}`)\n'
            f'Владелец *{owner.name}* (`{owner.uid}`)\n'
            f'Человек *{await group.members.all().count()}/{config.Constants.group_members_limit}*\n'
            f'Пердежы: *{["Выключены", "Включены"][group.notify_perdish]}*\n\n'
            f'_Создана {group.created_at}_\n\n'
            f'Ссылка-приглашение:\n`{invite_link}`')

    has_access = owner == user or user.admin
    if not has_access:
        text = '\n'.join(text.splitlines()[:3])

    if callback is None:
        await config.bot.edit_message_text(text, chat_id, message_id,
                                           reply_markup=groups_keyboard.get_group(group.pk, has_access, owner != user))
        return

    await callback.message.edit_text(text,
                                     reply_markup=groups_keyboard.get_group(group.pk, has_access, owner != user))


@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'password'))
async def change_group_password(callback: types.CallbackQuery, group: Group, user: User, state: FSMContext):
    group.password = Group.generate_password()
    await group.save()

    await callback.answer('Пароль группы изменен.')
    await show_group(callback, group, user, state)


@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'perdish'))
async def change_group_password(callback: types.CallbackQuery, group: Group, user: User, state: FSMContext):
    group.notify_perdish = not group.notify_perdish
    await group.save()

    await callback.answer(f'Пердежи {["вы", "в"][group.notify_perdish]}ключены.')
    await show_group(callback, group, user, state)


@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'name'))
async def change_group_name(callback: types.CallbackQuery, group: Group, state: FSMContext):
    await callback.message.edit_text(
        'Напишите новое название для вашей группы. Оно должно быть не длиннее 32 символов и не содержать специальных символов.')

    await state.set_state(NamingGroupStates.writing_name)
    await state.update_data({'last_msg': callback.message.message_id})
    await state.update_data({'group_id': group.pk})


@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'delete'))
async def delete_group(callback: types.CallbackQuery, group: Group, state: FSMContext):
    await callback.message.edit_text(f'Вы уверены что хотите удалить группу *{group.name}* (`{group.pk}`)?\n'
                                     f'Если вы уверены, тогда напишите название группы ответным сообщением.',
                                     reply_markup=groups_keyboard.get_group_return(group.pk, 'Отменить'))

    await state.set_state(DeleteGroupStates.writing_name)
    await state.update_data({'last_msg': callback.message.message_id})
    await state.update_data({'group_id': group.pk})


@router.message(DeleteGroupStates.writing_name)
async def delete_group_submit(message: types.Message, state: FSMContext, user: User):
    state_data = (await state.get_data())
    last_msg = state_data.get('last_msg')
    group_id = state_data.get('group_id')

    await message.delete()

    group = await Group.filter(pk=group_id).get()
    if group.name != message.text:
        info_message = await message.answer('Вы написали название группы неверно.')

    else:
        await group.delete()
        await state.clear()

        info_message = await message.answer(f'Группа *{group.name}* удалена.')
        await config.bot.edit_message_text('Выберите группу.', user.uid, last_msg,
                                           reply_markup=await groups_keyboard.get_all(user))

    await asyncio.sleep(3)
    await info_message.delete()


@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'members'))
async def group_members(callback: types.CallbackQuery, group: Group):
    await callback.message.edit_text('Выберете участника.',
                                     reply_markup=await groups_keyboard.get_group_members(group))


@router.callback_query(groups_keyboard.DeleteGroupMemberCallback.filter(F.submit == False))
async def call_submit_delete_group_member(callback: types.CallbackQuery):
    group_data = groups_keyboard.DeleteGroupMemberCallback.unpack(callback.data)

    await callback.message.edit_text(f'Вы уверены что хотите удалить пользователя с айди `{group_data.uid}`?',
                                     reply_markup=groups_keyboard.get_group_delete_member(group_data.uid, group_data.group))


@router.callback_query(groups_keyboard.DeleteGroupMemberCallback.filter(F.submit == True))
async def call_submit_delete_group_member(callback: types.CallbackQuery, user: User):
    group_data = groups_keyboard.DeleteGroupMemberCallback.unpack(callback.data)

    group = await Group.filter(pk=group_data.group).get()
    if group.owner_id == group_data.uid:
        await callback.answer('Вы не можете удалить создателя из группы.')

    elif user.pk == group_data.uid:
        await callback.answer('Вы не можете удалить самого себя из группы.')

    else:
        await group.members.remove(await User.filter(pk=group_data.uid).get())
        await config.bot.send_message(group_data.uid, f'Вы исключены из групппы *{group.name}* (`{group.pk}`)')

    await group_members(callback, group)


@router.callback_query(groups_keyboard.GroupCallback.filter(F.action == 'leave'))
async def leave_from_group(callback: types.CallbackQuery, group: Group, user: User, state: FSMContext):
    await group.members.remove(user)
    await callback.answer('Вы успешно покинули группу.')
    await groups_menu_callback(callback, user, state)

    owner = await group.owner

    await config.bot.send_message(owner.uid, f'Пользователь *{user.name}* (`{user.uid}`) покинул группу *{group.name}* (`{group.pk}`)')

