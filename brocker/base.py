from typing import Optional

import aiormq
from aiormq.abc import AbstractConnection, AbstractChannel

import config


class ConnectionStorer:
    _connection: Optional[AbstractConnection] = None
    _channel: Optional[AbstractChannel] = None

    async def get_connection(self) -> Optional[AbstractConnection]:
        if self._connection is None or self._connection.is_closed:
            self._connection = await aiormq.connect(config.AMQP.uri)

        return self._connection

    async def get_channel(self) -> Optional[AbstractChannel]:
        if self._channel is None or self._channel.is_closed:
            self._channel = await (await self.get_connection()).channel()
        return self._channel


storer = ConnectionStorer()
