from aiogram import Router

from . import ban
from . import notify
from . import whois
from . import send

router = Router()

router.include_router(ban.router)
router.include_router(notify.router)
router.include_router(whois.router)
router.include_router(send.router)
