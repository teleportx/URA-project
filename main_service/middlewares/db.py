from abc import ABC
from typing import Any, Dict, Callable

import tortoise.transactions
from aiogram.types import Update

from main_service.middlewares.util import UtilMiddleware


class DatabaseMiddleware(UtilMiddleware, ABC):
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with tortoise.transactions.in_transaction():
            return await handler(event, data)
