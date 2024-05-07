from aiogram import Router

from . import setnickname
from . import autoend

router = Router()

router.include_router(setnickname.router)
router.include_router(autoend.router)
