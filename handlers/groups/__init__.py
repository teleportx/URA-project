from aiogram import Router

from . import control
from . import join_group

router = Router()

router.include_router(control.router)
router.include_router(join_group.router)
