from aiogram import Router

from . import start
from . import srat
from . import other_commands

router = Router()

router.include_router(start.router)
router.include_router(srat.router)
router.include_router(other_commands.router)
