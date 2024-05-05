from aiogram import Router

from . import cancel
from . import admin
from . import info
from . import groups
from . import srat
from . import start
from . import setnickname
from . import report

router = Router()

router.include_router(cancel.router)
router.include_router(start.router)
router.include_router(srat.router)
router.include_router(info.router)
router.include_router(admin.router)
router.include_router(groups.router)
router.include_router(setnickname.router)
router.include_router(report.router)
