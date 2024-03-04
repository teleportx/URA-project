from aiogram import Router

from . import notify
from . import credits

router = Router()

router.include_router(notify.router)
router.include_router(credits.router)
