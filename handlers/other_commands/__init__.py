from aiogram import Router

from . import link
from . import notify
from . import settings
from . import user_control

router = Router()

router.include_router(link.router)
router.include_router(notify.router)
router.include_router(settings.router)
router.include_router(user_control.router)
