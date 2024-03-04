from aiogram import Router

from . import notify
from . import credits
from . import ban

router = Router()

router.include_router(notify.router)
router.include_router(credits.router)
router.include_router(ban.router)
