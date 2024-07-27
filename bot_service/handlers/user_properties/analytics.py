from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject
from asyncpg import Record
from tortoise import Tortoise

import config
from db.ToiletSessions import SretSession
from db.User import User

router = Router()

stat_request = '''SELECT sret_type,
                            autoend,    
                            start >= (now() - interval '1 week') as last_week,
                            start >= (now() - interval '1 month') as last_month,
                            AVG(s.end - s.start),
                            COUNT(*)
                  FROM sretsession as s
                           WHERE user_id = %d   
                           GROUP BY sret_type, last_week, last_month, autoend;'''


def calc_avg(var, el):
    seconds =  el['avg'].total_seconds()
    if var[0] is None:
        var = (seconds, el['count'])

    else:
        total = var[1] + el['count']
        var = ((var[0] * var[1] + seconds * el['count']) / total, total)

    return var


def render_time(val):
    if val[0] is None:
        return 'Н/Д'

    return f'{round(val[0] / 60, 1)} минут'


@router.message(Command("anal"))
async def anal(message: types.Message, command: CommandObject, user: User):
    user_id = user.uid
    if user.admin and command.args is not None and command.args.isnumeric():
        user_id = int(command.args)

    conn = Tortoise.get_connection('default')
    res = await conn.execute_query(stat_request % user_id)

    co = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    avg = [(None, 0), (None, 0), (None, 0)]
    for el in res[1]:
        crit = not el['autoend'] and el['sret_type'] != 3
        if el['last_week']:
            co[0][el['sret_type'] - 1] += el['count']
            if crit:
                avg[0] = calc_avg(avg[0], el)

        if el['last_month']:
            co[1][el['sret_type'] - 1] += el['count']
            if crit:
                avg[1] = calc_avg(avg[1], el)

        co[2][el['sret_type'] - 1] += el['count']
        if crit:
            avg[2] = calc_avg(avg[2], el)

    pronouns = 'вы'
    if user.uid != user_id:
        pronouns = str(user_id)

    text = (
            f'<b>Всего за все время {pronouns}:</b>\n'
            f'Раз срали: <code>{co[2][0]}</code>\n'
            f'Раз дристали: <code>{co[2][1]}</code>\n'
            f'Пернули: <code>{co[2][2]}</code>\n'
            f'Среднее время в туалете: <code>{render_time(avg[0])}</code>\n\n'
            
            f'<b>За последний месяц {pronouns}:</b>\n'
            f'Раз срали: <code>{co[1][0]}</code>\n'
            f'Раз дристали: <code>{co[1][1]}</code>\n'
            f'Пернули: <code>{co[1][2]}</code>\n'
            f'Среднее время в туалете: <code>{render_time(avg[1])}</code>\n\n'
            
            f'<b>За последнюю неделю {pronouns}:</b>\n'
            f'Раз срали: <code>{co[0][0]}</code>\n'
            f'Раз дристали: <code>{co[0][1]}</code>\n'
            f'Пернули: <code>{co[0][2]}</code>\n'
            f'Среднее время в туалете: <code>{render_time(avg[2])}</code>\n\n'
            
            f'Аккаунт создан: <code>{user.created_at}</code>\n'
    )

    await message.reply(text)
