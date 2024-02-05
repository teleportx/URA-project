from aiogram import Router

from . import start
from . import srat
from . import other_commands
from . import group_perdish

router = Router()

router.include_router(start.router)
router.include_router(srat.router)
router.include_router(group_perdish.router)
router.include_router(other_commands.router)
