from aiogram import Router

from . import notify
from . import user_control
from . import credits

router = Router()

router.include_router(notify.router)
router.include_router(user_control.router)
router.include_router(credits.router)
