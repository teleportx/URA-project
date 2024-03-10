from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.User import User
from db.UserUnion import Group


class GroupCallback(CallbackData, prefix="grp"):
    group: int
    action: str


class DeleteGroupMemberCallback(CallbackData, prefix="grpdm"):
    uid: int
    group: int
    submit: bool


def _return_button(text: str = 'Назад'):
    return InlineKeyboardButton(
        text=text,
        callback_data=GroupCallback(group=-1, action='main').pack()
    )


def _group_button(text: str, group_id: int):
    return InlineKeyboardButton(
            text=text,
            callback_data=GroupCallback(group=group_id, action='show').pack()
        )


def get_return(text: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_return_button(text))

    return kb.as_markup()


def get_group_return(group_id: int, text: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_group_button(text, group_id))

    return kb.as_markup()


async def get_all(user: User) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(
        text='Создать',
        callback_data=GroupCallback(group=-1, action='create').pack()
    ))

    async for group in user.groups_member:
        text = 'O| ' * (await group.owner == user)
        kb.row(_group_button(text + group.name, group.pk))

    return kb.as_markup()


def get_group(group_id: int, owned: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_return_button())

    if not owned:
        kb.add(InlineKeyboardButton(
            text='Покинуть',
            callback_data=GroupCallback(group=group_id, action='leave').pack()
        ))

        return kb.as_markup()

    kb.add(InlineKeyboardButton(
        text='Участники',
        callback_data=GroupCallback(group=group_id, action='members').pack()
    ))

    kb.row(InlineKeyboardButton(
        text='Изменить пароль',
        callback_data=GroupCallback(group=group_id, action='password').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Изменить имя',
        callback_data=GroupCallback(group=group_id, action='name').pack()
    ))

    kb.row(InlineKeyboardButton(
        text='Удалить группу',
        callback_data=GroupCallback(group=group_id, action='delete').pack()
    ))

    return kb.as_markup()


async def get_group_members(group: Group) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(_group_button('Назад', group.pk))

    async for member in group.members.all():
        kb.add(InlineKeyboardButton(
            text=member.name,
            callback_data=DeleteGroupMemberCallback(uid=member.pk, group=group.pk, submit=False).pack()
        ))

    kb.adjust(1, 3)

    return kb.as_markup()


def get_group_delete_member(uid: int, group_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(
        text='Отмена',
        callback_data=GroupCallback(group=group_id, action='members').pack()
    ))

    kb.add(InlineKeyboardButton(
        text='Удалить',
        callback_data=DeleteGroupMemberCallback(uid=uid, group=group_id, submit=True).pack()
    ))

    return kb.as_markup()
