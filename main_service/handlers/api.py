import aiogram
from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from tortoise.exceptions import ValidationError

import config
from db.ApiAuth import ApiToken, TokenNameValidator
from db.User import User
from keyboards import api_keyboard

router = Router()

menu_text = ('<b>Меню управления API токенами</b>\n'
             'Для того чтобы отозвать токен нажмите на него.\n\n'
             '<a href="https://avatars.mds.yandex.net/get-vertis-journal/4466156/2021-04-15-bf7b6ac10d6547e7befb72eb810aa671.jpeg_1622737360694/439x439">Документация к API.</a>')

requirements_text = ('<b>Название должно соответствовать данным условиям:</b>\n'
                     '  - Длина от 3 до 64 символов\n'
                     '  - Cимволы могут быть только строчными латинскими буквами, цифрами и нижними подчеркиваниями\n')

class NewTokenStates(StatesGroup):
    writing_name = State()


@router.message(Command("api"))
async def api_menu(message: types.Message, user: User, command: CommandObject):
    if command.args is not None:
        await message.delete()

        hashed_token = ApiToken.hash_token(command.args)
        token = await ApiToken.get_or_none(token=hashed_token)

        if token is None:
            await message.answer('Токен не найден.')
            return

        await message.answer(f'<b>Токен {token.name}</b>\n\n'
                             f'Owner: <code>{token.owner_id}</code>\n'
                             f'ID: <code>{token.id}</code>\n'
                             f'Valid: <code>{["No", "Yes"][token.valid]}</code>\n'
                             f'Created at: <code>{token.created_at}</code>')

        return

    await message.answer(menu_text, reply_markup=await api_keyboard.get(user))


@router.callback_query(api_keyboard.ApiCallback.filter(F.action == 'menu'))
async def api_menu_button(callback: types.CallbackQuery, user: User):
    await callback.message.edit_text(menu_text, reply_markup=await api_keyboard.get(user))


@router.callback_query(api_keyboard.ApiCallback.filter(F.action == 'revoke'))
async def revoke_api_token(callback: types.CallbackQuery):
    unpacked_data = api_keyboard.ApiCallback.unpack(callback.data)

    token_name = ''
    for button in callback.message.reply_markup.inline_keyboard:
        if button[0].callback_data == callback.data:
            token_name = button[0].text

    await callback.message.edit_text(f'Вы уверены, что хотите отозвать токен <code>{token_name}</code>?\n'
                                     f'Это действие нельзя отменить.',
                                     reply_markup=api_keyboard.get_revoke_submit(unpacked_data.token))


@router.callback_query(api_keyboard.ApiCallback.filter(F.action == 'revoke_submit'))
async def revoke_api_token_submit(callback: types.CallbackQuery, user: User):
    unpacked_data = api_keyboard.ApiCallback.unpack(callback.data)

    await ApiToken.filter(pk=unpacked_data.token).update(valid=False)

    text = callback.message.html_text
    token_name = text[text.find('<code>') + 6:text.find('</code>')]

    await callback.answer(f'Токен {token_name} отозван.')
    await api_menu_button(callback, user)


@router.callback_query(api_keyboard.ApiCallback.filter(F.action == 'new'))
async def new_api_token(callback: types.CallbackQuery, user: User, state: FSMContext):
    if await user.tokens_owned.filter(valid=True).count() >= config.Constants.max_api_tokens:
        await callback.answer(f'Вы не можете создать более чем {config.Constants.max_api_tokens} токенов.', show_alert=True)
        return

    await state.set_state(NewTokenStates.writing_name)
    await state.update_data(last_msg=callback.message.message_id)

    await callback.message.edit_text('Напишите название токена.\n\n' + requirements_text)


@router.message(NewTokenStates.writing_name)
async def new_api_token_wrote_name(message: types.Message, user: User, state: FSMContext, bot: Bot):
    await message.delete()

    token_name = message.text
    last_msg = (await state.get_data()).get('last_msg')

    if not(3 <= len(token_name) <= 64):
        try:
            await bot.edit_message_text('Недопустимая длина названия.\n\n' + requirements_text, message.chat.id, last_msg)

        except aiogram.exceptions.TelegramBadRequest:
            await bot.edit_message_text('Недопустимая длина названия\n\n' + requirements_text, message.chat.id, last_msg)

        return

    try:
        TokenNameValidator()(token_name)

    except ValidationError as e:
        try:
            await bot.edit_message_text(f'Недопустимый символ на позиции {e.args[1] + 1}.\n\n' + requirements_text, message.chat.id, last_msg)

        except aiogram.exceptions.TelegramBadRequest:
            await bot.edit_message_text(f'Недопустимый символ на позиции {e.args[1] + 1}\n\n' + requirements_text, message.chat.id, last_msg)

        return

    await state.clear()

    secret, hashed_secret = ApiToken.generate_token()
    token = await ApiToken.create(token=hashed_secret, name=token_name, owner=user)

    await bot.edit_message_text(menu_text, message.chat.id, last_msg, reply_markup=await api_keyboard.get(user))

    await message.answer(f'<b>Токен {token.name}</b>\n\n'
                         f'ID:\n<code>{token.id}</code>\n'
                         f'TOKEN:\n<span class="tg-spoiler">{secret}</span>\n\n'
                         f'Created at: <code>{token.created_at}</code>')
