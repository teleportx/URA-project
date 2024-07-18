import json
from abc import ABC
from typing import Any, Dict, Callable


from aiogram.types import Update
from loguru import logger
from pydantic import BaseModel

import config
from bot_service.middlewares.util import UtilMiddleware


class DegradationData(BaseModel):
    admin_only: bool = False
    enable_groups: bool = True
    enable_channels: bool = True


class DegradationMiddleware(UtilMiddleware, ABC):
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        degrade = DegradationData(**json.loads(await config.storage.redis.get('degrade')))
        data['degrade'] = degrade

        if degrade.admin_only and not data['user'].admin:
            return

        if degrade.admin_only:
            logger.info('Pass admin under "admin_only" degradation')

        return await handler(event, data)
