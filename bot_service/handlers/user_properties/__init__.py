from aiogram import Router

from . import setnickname
from . import autoend
from . import analytics

router = Router()

router.include_router(setnickname.router)
router.include_router(autoend.router)
router.include_router(analytics.router)
