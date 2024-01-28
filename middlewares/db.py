from abc import ABC
from typing import Any, Dict, Callable

from aiogram.types import Update

from db.base import db
from middlewares.util import UtilMiddleware


class DatabaseMiddleware(UtilMiddleware, ABC):
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        with db:
            return await handler(event, data)
