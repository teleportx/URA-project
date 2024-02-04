from aiogram import Router

from handlers import start
from handlers import srat
from handlers import notify
from handlers import user_control
from handlers import settings
from handlers import group_perdish
from handlers import link

router = Router()

router.include_router(start.router)
router.include_router(srat.router)
router.include_router(notify.router)
router.include_router(user_control.router)
router.include_router(settings.router)
router.include_router(group_perdish.router)
router.include_router(link.router)
