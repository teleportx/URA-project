from typing import Optional

import aiormq
from aiormq.abc import AbstractConnection

import config


class ConnectionStorer:
    _connection: Optional[AbstractConnection] = None

    async def get_connection(self) -> Optional[AbstractConnection]:
        if self._connection is None or self._connection.is_closed:
            self._connection = await aiormq.connect(config.AMQP.uri)

        return self._connection


storer = ConnectionStorer()
