from aiogram import Router

from . import setnickname
from . import autoend
from . import analytics
from . import export

router = Router()

router.include_router(setnickname.router)
router.include_router(autoend.router)
router.include_router(analytics.router)
router.include_router(export.router)
