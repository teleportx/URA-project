from aiogram import Router

from handlers import start

router = Router()

router.include_router(start.router)
