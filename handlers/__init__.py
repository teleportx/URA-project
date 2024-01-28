from aiogram import Router

from handlers import start
from handlers import srat
from handlers import notify
from handlers import user_control

router = Router()

router.include_router(start.router)
router.include_router(srat.router)
router.include_router(notify.router)
router.include_router(user_control.router)
