from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, CommandObject, MagicData

import config
from db.User import User
from db.UserUnion import Group
from keyboards.group import join_group_keyboard

router = Router()


@router.message(Command("start"), MagicData(F.command.args.startswith('IG')))
async def join_group(message: types.Message, command: CommandObject, user: User):
    try:
        group_id, group_password = command.args.replace('IG', '').split('P')[:2]

    except ValueError:
        return

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
                                  f'Пользователь <b>{user.name}</b> (<code>{user.uid}</code>) хочет вступить к вам в группу <b>{group.name}</b> (<code>{group.pk}</code>)',
                                  reply_markup=join_group_keyboard.get(user.uid, group.pk))

    text = ''
    if (await user.groups_member.all().count() + await user.groups_requested.all().count()) > config.Constants.member_group_limit:
        text = '\n\n<i>Учтите, что при принять все поданные вами заявки не получится, так как вы достигните лимит групп.</i>'

    await message.reply(f'Ваша заявка на присоединение к группе <b>{group.name}</b> отправлена и ожидает одобрения.' + text)


@router.callback_query(join_group_keyboard.JoinGroupCallback.filter())
async def join_group_decline(callback: types.CallbackQuery):
    join_group_data = join_group_keyboard.JoinGroupCallback.unpack(callback.data)

    group = await Group.filter(pk=join_group_data.group_id).get()

    join_user = await User.filter(pk=join_group_data.uid).get()
    await group.requests.remove(join_user)
    if join_group_data.result and (await group.members.all().count()) >= config.Constants.group_members_limit:
        await callback.answer('Вы достигли максимум человек в группе.',
                              show_alert=True)
        return

    request_status = ["ОТКЛОНЕНА", "ОДОБРЕНА"][join_group_data.result]
    text = f'Пользователь <b>{join_user.name}</b> (`{join_user.uid}`) хочет вступить к вам в группу <b>{group.name}</b> (<code>{group.pk}</code>)'

    await callback.message.edit_text(text + f'\n\n<b>{request_status}</b>')
    join_user_message = await config.bot.send_message(join_group_data.uid, f'Ваша заявкам в группу <b>{group.name} {request_status}</b>')

    if not join_group_data.result:
        return

    if not join_user.admin and await join_user.groups_member.all().count() >= config.Constants.member_group_limit:
        await callback.answer('Пользователь не добавлен в группу так как количество групп к котором он присоединен достигло максимума.',
                              show_alert=True)
        await callback.message.edit_text(text + f'\n\n<b>{request_status} НЕ ДОБАВЛЕН</b> (лимит групп)')

        await join_user_message.reply('Вы не были в группу так как количество групп к котором вы присоединенились достигло максимума.')
        return

    await group.members.add(join_user)
