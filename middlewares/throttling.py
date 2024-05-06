from abc import ABC
from datetime import datetime
from typing import Any, Dict, Callable

from aiogram.types import Update

import config
from middlewares.util import UtilMiddleware


class ThrottlingMiddleware(UtilMiddleware, ABC):
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user_id = self.get_user(event).id

        last_act = float(await config.storage.redis.get(user_id))
        if last_act is None:
            last_act = 0

        now = datetime.now().timestamp()
        if (now - last_act) <= config.Constants.throttling_time:
            return

        await config.storage.redis.set(user_id, now)
        return await handler(event, data)
