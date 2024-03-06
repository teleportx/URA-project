from aiogram import Router

from . import admin
from . import credits
from . import groups
from . import srat
from . import start

router = Router()

router.include_router(start.router)
router.include_router(srat.router)
router.include_router(credits.router)
router.include_router(admin.router)
router.include_router(groups.router)
