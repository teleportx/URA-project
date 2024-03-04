from abc import ABC
from typing import Any, Dict, Callable

from aiogram.types import Update

import tortoise.transactions
from middlewares.util import UtilMiddleware


class DatabaseMiddleware(UtilMiddleware, ABC):
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with tortoise.transactions.in_transaction():
            return await handler(event, data)
