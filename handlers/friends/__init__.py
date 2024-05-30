from aiogram import Router

from . import control
from . import request

router = Router()

router.include_router(control.router)
router.include_router(request.router)
