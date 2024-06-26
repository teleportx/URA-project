from aiogram import Router

from . import control
from . import join

router = Router()

router.include_router(control.router)
router.include_router(join.router)
