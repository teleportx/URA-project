from aiogram import Router

from . import control

router = Router()

router.include_router(control.router)
