from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject

import config
from db.User import User
from db.UserUnion import Group
from filters.command_args import CommandArgsStartswith
from keyboards.group import join_group_keyboard

router = Router()


@router.message(Command("start"), CommandArgsStartswith('IG'))
async def join_group(message: types.Message, command: CommandObject, user: User):
    group_id, group_password = command.args.replace('IG', '').split('P')[:2]

    if not group_id.isnumeric() or not group_password.isnumeric():
        await message.reply('Группа не найдена.')
        return

    group_id = int(group_id)
    group_password = int(group_password)

    group = await Group.filter(pk=group_id, password=group_password).get_or_none()
    if group is None:
        await message.reply('Группа не найдена.')
        return

    if await group.members.filter(uid=user.uid).exists():
        await message.reply('Вы уже состоите в этой группе.')
        return

    if await group.requests.filter(uid=user.uid).exists():
        await message.reply('Вы уже подавали заявку для этой группы.')
        return

    await group.requests.add(user)
    await config.bot.send_message((await group.owner.only('uid').get()).uid,
                                  f'Пользователь *{user.name}* (`{user.uid}`) хочет вступить к вам в группу *{group.name}* (`{group.pk}`)',
                                  reply_markup=join_group_keyboard.get(user.uid, group.pk))

    text = ''
    if (await user.groups_member.all().count() + await user.groups_requested.all().count()) > 5:
        text = '\n\n_Учтите, что при принять все поданные вами заявки не получится, так как вы достигните лимит групп._'

    await message.reply(f'Ваша заявка на присоединение к группе *{group.name}* отправлена и ожидает одобрения.' + text)


@router.callback_query(join_group_keyboard.JoinGroupCallback.filter())
async def join_group_decline(callback: types.CallbackQuery):
    join_group_data = join_group_keyboard.JoinGroupCallback.unpack(callback.data)

    group = await Group.filter(pk=join_group_data.group_id).get()

    join_user = await User.filter(pk=join_group_data.uid).get()
    await group.requests.remove(join_user)
    if join_group_data.result and (await group.members.all().count()) >= 1:
        await callback.answer('Вы достигли максимум человек в группе.',
                              show_alert=True)
        return

    request_status = ["ОТКЛОНЕНА", "ОДОБРЕНА"][join_group_data.result]
    text = f'Пользователь *{join_user.name}* (`{join_user.uid}`) хочет вступить к вам в группу *{group.name}* (`{group.pk}`)'

    await callback.message.edit_text(text + f'\n\n*{request_status}*')
    join_user_message = await config.bot.send_message(join_group_data.uid, f'Ваша заявкам в группу *{group.name} {request_status}*')

    if not join_group_data.result:
        return

    if not join_user.admin and await join_user.groups_member.all().count() >= 5:
        await callback.answer('Пользователь не добавлен в группу так как количество групп к котором он присоединен достигло максимума.',
                              show_alert=True)
        await callback.message.edit_text(text + f'\n\n*{request_status} НЕ ДОБАВЛЕН* (лимит групп)')

        await join_user_message.reply('Вы не были в группу так как количество групп к котором вы присоединенились достигло максимума.')
        return

    await group.members.add(join_user)
