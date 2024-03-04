from aiogram import Router

from . import notify
from . import user_control

router = Router()

router.include_router(notify.router)
router.include_router(user_control.router)
