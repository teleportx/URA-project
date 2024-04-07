from aiogram import Router

from . import ban
from . import notify
from . import whois

router = Router()

router.include_router(ban.router)
router.include_router(notify.router)
router.include_router(whois.router)
