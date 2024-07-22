import sys

sys.path.append('..')
sys.path.append('../..')

from typing import Optional

from aiogram import Bot
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

import brocker
import config
import db
import api_middlewares
import setup_logger
from db.ToiletSessions import SretSession, SretType
from db.User import User
from utils import send_srat_notification

setup_logger.__init__("API srat")

app = FastAPI(docs_url=None, redoc_url=None)
api_middlewares.setup(app, True)


class SratModel(BaseModel):
    status: Optional[SretType]


@app.on_event("startup")
async def startup_event():
    await db.init()
    await brocker.init()

    bot = Bot(
        token=config.Telegram.token,
        parse_mode='html',
    )
    config.bot = bot


@app.get('/api/srat/', status_code=200, response_model=SratModel)
async def get_srat(request: Request):
    user: User = request.state.user

    last_open_session = await SretSession.filter(user=user, end=None).get_or_none()
    if last_open_session is None:
        srat_status = None

    else:
        srat_status = last_open_session.sret_type

    return SratModel(status=srat_status)


@app.post('/api/srat', status_code=204)
async def set_srat(request: Request, srat: SratModel):
    if srat.status is None:
        srat.status = 0

    user: User = request.state.user

    if not await send_srat_notification.verify_action(user, srat.status):
        return JSONResponse({"detail": "You cannot make this action"}, status_code=400)

    await send_srat_notification.send(user, srat.status)
    return
