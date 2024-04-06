from aiogram import Router

from . import ban
from . import notify

router = Router()

router.include_router(ban.router)
router.include_router(notify.router)
